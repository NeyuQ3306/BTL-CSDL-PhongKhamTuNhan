from clinic_app.sql import statements


def test_statements_preserves_semicolons_in_mysql_quoted_tokens():
    sql = r"""-- Staff DDL; keep the same connection
SET @ddl = 'SELECT ''a;b'' AS quoted, \'c;d\' AS escaped'; # another ; comment
/* ; block comment */ SELECT "e;f", `g``;h`;
SELECT 2- -1
"""
    assert list(statements(sql)) == [
        r"SET @ddl = 'SELECT ''a;b'' AS quoted, \'c;d\' AS escaped'",
        'SELECT "e;f", `g``;h`',
        'SELECT 2- -1',
    ]


def test_statements_keeps_executable_comments_and_optimizer_hints():
    assert list(statements('/*!80000 SET @value = 1 */; SELECT /*+ NO_MERGE(t) */ 1;')) == [
        '/*!80000 SET @value = 1 */',
        'SELECT /*+ NO_MERGE(t) */ 1',
    ]
