boolean IfNotExistsOpt() :
{
}
{
    <IF> <NOT> <EXISTS> { return true; }
|
    { return false; }
}

boolean IfExistsOpt() :
{
}
{
    <IF> <EXISTS> { return true; }
|
    { return false; }
}

SqlCreate SqlCreateSchema(Span s, boolean replace) :
{
    final boolean ifNotExists;
    final SqlIdentifier id;
}
{
    <SCHEMA> ifNotExists = IfNotExistsOpt() id = CompoundIdentifier()
    {
        return SqlDdlNodes.createSchema(s.end(this), replace, ifNotExists, id);
    }
}

SqlCreate SqlCreateDatabase(Span s, boolean replace) :
{
    final SqlIdentifier id;
}
{
    <DATABASE> id = CompoundIdentifier()
    {
        return SqlDdlNodes.createDatabase(s.end(this), id);
    }
}

SqlCreate SqlCreateForeignSchema(Span s, boolean replace) :
{
    final boolean ifNotExists;
    final SqlIdentifier id;
    SqlNode type = null;
    SqlNode library = null;
    SqlNodeList optionList = null;
}
{
    <FOREIGN> <SCHEMA> ifNotExists = IfNotExistsOpt() id = CompoundIdentifier()
    (
         <TYPE> type = StringLiteral()
    |
         <LIBRARY> library = StringLiteral()
    )
    [ optionList = Options() ]
    {
        return SqlDdlNodes.createForeignSchema(s.end(this), replace,
            ifNotExists, id, type, library, optionList);
    }
}

SqlNodeList Options() :
{
    final Span s;
    final List<SqlNode> list = Lists.newArrayList();
}
{
    <OPTIONS> { s = span(); } <LPAREN>
    [
        Option(list)
        (
            <COMMA>
            Option(list)
        )*
    ]
    <RPAREN> {
        return new SqlNodeList(list, s.end(this));
    }
}

void Option(List<SqlNode> list) :
{
    final SqlIdentifier id;
    final SqlNode value;
}
{
    id = SimpleIdentifier()
    value = Literal() {
        list.add(id);
        list.add(value);
    }
}

SqlNodeList TableElementList() :
{
    final Span s;
    final List<SqlNode> list = Lists.newArrayList();
}
{
    <LPAREN> { s = span(); }
    TableElement(list)
    (
        <COMMA> TableElement(list)
    )*
    <RPAREN> {
        return new SqlNodeList(list, s.end(this));
    }
}

void TableElement(List<SqlNode> list) :
{
    final SqlIdentifier id;
    final SqlDataTypeSpec type;
    final boolean nullable;
    final SqlNode e;
    final SqlNode constraint;
    SqlIdentifier name = null;
    final SqlNodeList columnList;
    final Span s = Span.of();
    final ColumnStrategy strategy;
}
{
    id = SimpleIdentifier()
    (
        type = DataType()
        (
            <NULL> { nullable = true; }
        |
            <NOT> <NULL> { nullable = false; }
        |
            { nullable = true; }
        )
        (
            [ <GENERATED> <ALWAYS> ] <AS> <LPAREN>
            e = Expression(ExprContext.ACCEPT_SUB_QUERY) <RPAREN>
            (
                <VIRTUAL> { strategy = ColumnStrategy.VIRTUAL; }
            |
                <STORED> { strategy = ColumnStrategy.STORED; }
            |
                { strategy = ColumnStrategy.VIRTUAL; }
            )
        |
            <DEFAULT_> e = Expression(ExprContext.ACCEPT_SUB_QUERY) {
                strategy = ColumnStrategy.DEFAULT;
            }
        |
            {
                e = null;
                strategy = nullable ? ColumnStrategy.NULLABLE
                    : ColumnStrategy.NOT_NULLABLE;
            }
        )
        {
            list.add(
                SqlDdlNodes.column(s.add(id).end(this), id,
                    type.withNullable(nullable), e, strategy));
        }
    |
        { list.add(id); }
    )
|
    id = SimpleIdentifier() {
        list.add(id);
    }
|
    [ <CONSTRAINT> { s.add(this); } name = SimpleIdentifier() ]
    (
        <CHECK> { s.add(this); } <LPAREN>
        e = Expression(ExprContext.ACCEPT_SUB_QUERY) <RPAREN> {
            list.add(SqlDdlNodes.check(s.end(this), name, e));
        }
    |
        <UNIQUE> { s.add(this); }
        columnList = ParenthesizedSimpleIdentifierList() {
            list.add(SqlDdlNodes.unique(s.end(columnList), name, columnList));
        }
    |
        <PRIMARY>  { s.add(this); } <KEY>
        columnList = ParenthesizedSimpleIdentifierList() {
            list.add(SqlDdlNodes.primary(s.end(columnList), name, columnList));
        }
    )
}

SqlCreate SqlCreateTable(Span s, boolean replace) :
{
    final boolean ifNotExists;
    final SqlIdentifier id;
    SqlNodeList tableElementList = null;
    SqlNode query = null;
}
{
    <TABLE> ifNotExists = IfNotExistsOpt() id = CompoundIdentifier()
    [ tableElementList = TableElementList() ]
    [ <AS> query = OrderedQueryOrExpr(ExprContext.ACCEPT_QUERY) ]
    {
        return SqlDdlNodes.createTable(s.end(this), replace, ifNotExists, id,
            tableElementList, query);
    }
}

SqlCreate SqlCreateParquetTable(Span s, boolean replace) :
{
    //TODO percy need to implement replace if not exists for create parquet table
    final SqlIdentifier name;
    final SqlNode folder;
    final SqlNode wildcard;
}
{
    <PARQUET> <TABLE> name = CompoundIdentifier()
    <LPAREN>
    folder = StringLiteral()
    <COMMA>
    wildcard = StringLiteral()
    <RPAREN> {
        return SqlDdlNodes.createParquetTable(s.end(this), name, folder, wildcard);
    }
}

SqlCreate SqlCreateView(Span s, boolean replace) :
{
    final SqlIdentifier id;
    SqlNodeList columnList = null;
    final SqlNode query;
}
{
    <VIEW> id = CompoundIdentifier()
    [ columnList = ParenthesizedSimpleIdentifierList() ]
    <AS> query = OrderedQueryOrExpr(ExprContext.ACCEPT_QUERY) {
        return SqlDdlNodes.createView(s.end(this), replace, id, columnList,
            query);
    }
}

SqlCreate SqlCreateMaterializedView(Span s, boolean replace) :
{
    final boolean ifNotExists;
    final SqlIdentifier id;
    SqlNodeList columnList = null;
    final SqlNode query;
}
{
    <MATERIALIZED> <VIEW> ifNotExists = IfNotExistsOpt()
    id = CompoundIdentifier()
    [ columnList = ParenthesizedSimpleIdentifierList() ]
    <AS> query = OrderedQueryOrExpr(ExprContext.ACCEPT_QUERY) {
        return SqlDdlNodes.createMaterializedView(s.end(this), replace,
            ifNotExists, id, columnList, query);
    }
}

SqlDrop SqlDropSchema(Span s, boolean replace) :
{
    final boolean ifExists;
    final SqlIdentifier id;
    final boolean foreign;
}
{
    (
        <FOREIGN> { foreign = true; }
    |
        { foreign = false; }
    )
    <SCHEMA> ifExists = IfExistsOpt() id = CompoundIdentifier() {
        return SqlDdlNodes.dropSchema(s.end(this), foreign, ifExists, id);
    }
}

SqlDrop SqlDropDatabase(Span s, boolean replace) :
{
    final boolean ifExists;
    final SqlIdentifier id;
}
{
    <DATABASE> ifExists = IfExistsOpt() id = CompoundIdentifier() {
        return SqlDdlNodes.dropDatabase(s.end(this), ifExists, id);
    }
}

SqlDrop SqlDropTable(Span s, boolean replace) :
{
    final boolean ifExists;
    final SqlIdentifier id;
}
{
    <TABLE> ifExists = IfExistsOpt() id = CompoundIdentifier() {
        return SqlDdlNodes.dropTable(s.end(this), ifExists, id);
    }
}

SqlDrop SqlDropView(Span s, boolean replace) :
{
    final boolean ifExists;
    final SqlIdentifier id;
}
{
    <VIEW> ifExists = IfExistsOpt() id = CompoundIdentifier() {
        return SqlDdlNodes.dropView(s.end(this), ifExists, id);
    }
}

SqlDrop SqlDropMaterializedView(Span s, boolean replace) :
{
    final boolean ifExists;
    final SqlIdentifier id;
}
{
    <MATERIALIZED> <VIEW> ifExists = IfExistsOpt() id = CompoundIdentifier() {
        return SqlDdlNodes.dropMaterializedView(s.end(this), ifExists, id);
    }
}

// End parserImplsDdl.ftl
