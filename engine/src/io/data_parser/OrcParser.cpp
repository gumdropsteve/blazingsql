#include "OrcParser.h"

#include <arrow/io/file.h>

#include <blazingdb/io/Library/Logging/Logger.h>

#include <numeric>
#include "ArgsUtil.h"

namespace ral {
namespace io {

orc_parser::orc_parser(std::map<std::string, std::string> args_map_) : args_map{args_map_} {}

orc_parser::~orc_parser() {
	// TODO Auto-generated destructor stub
}

std::unique_ptr<ral::frame::BlazingTable> orc_parser::parse_batch(
	ral::io::data_handle handle,
	const Schema & schema,
	std::vector<int> column_indices,
	std::vector<cudf::size_type> row_groups)
{

	std::shared_ptr<arrow::io::RandomAccessFile> file = handle.file_handle;
	if(file == nullptr) {
		return schema.makeEmptyBlazingTable(column_indices);
	}
	if(column_indices.size() > 0) {
		// Fill data to orc_opts
		auto arrow_source = cudf::io::arrow_io_source{file};
		cudf::io::orc_reader_options orc_opts = getOrcReaderOptions(args_map, arrow_source);

		std::vector<std::string> col_names;
		col_names.resize(column_indices.size());

		for(size_t column_i = 0; column_i < column_indices.size(); column_i++) {
			col_names[column_i] = schema.get_name(column_indices[column_i]);
		}

		orc_opts.set_columns(col_names);
		orc_opts.set_stripes(row_groups);

		auto result = cudf::io::read_orc(orc_opts);

		return std::make_unique<ral::frame::BlazingTable>(std::move(result.tbl), result.metadata.column_names);
	}
	return nullptr;
}

void orc_parser::parse_schema(
	std::shared_ptr<arrow::io::RandomAccessFile> file, ral::io::Schema & schema) {

	auto arrow_source = cudf::io::arrow_io_source{file};
	cudf::io::orc_reader_options orc_opts = getOrcReaderOptions(args_map, arrow_source);
	orc_opts.set_num_rows(1);

	cudf::io::table_with_metadata table_out = cudf::io::read_orc(orc_opts);
	file->Close();

	for(cudf::size_type i = 0; i < table_out.tbl->num_columns() ; i++) {
		std::string name = table_out.metadata.column_names[i];
		cudf::type_id type = table_out.tbl->get_column(i).type().id();
		size_t file_index = i;
		bool is_in_file = true;
		schema.add_column(name, type, file_index, is_in_file);
	}
}

} /* namespace io */
} /* namespace ral */
