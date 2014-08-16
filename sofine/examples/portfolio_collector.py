# TODO
# - write code to perform useful queries with business rules
# - wrapper to update the data and report
# - cron somewhere


def _get_data(c, customer_id, p, password, a, account_id, e, email):
    import sofine.runner as runner
    import psycopg2
    
    # sofine pipeline to collect the data
    data = {}
    plugins = ['fidelity', 'ystockquotelib']
    plugin_groups = ['example', 'example']
    fidelity_args = [c, customer_id, p, password, a, account_id, e, email]
    plugin_args = [fidelity_args, []]
    
    data = runner.get_data_batch(data, plugins, plugin_groups, plugin_args)
    
    return data


def _store_data(insert_data, db_password):
    import psycopg2
    
    def report_db_error(e):
        print('Error code: {0}, Error: {1}, Dianostic severity: {2}, Diagnostic message: {3}'.format(
            e.pgcode, e.pgerror, e.diag.severity, e.diag.message_primary))
    
    db_name = 'sofine_portfolio'
    db_user = 'markweiss'
    
    conn = None
    conn_str = ''
    try:
        conn_str = "dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password)
        conn = psycopg2.connect(conn_str)
    except Exception as e:
        print('Failed to connect. Connection string: {0}'.format(conn_str))
        report_db_error(e)
        return

    cur = conn.cursor()
    # Create a list of tuples to create a bulk insert statement
    insert_data_str = ','.join(cur.mogrify('%s', (x, )) for x in insert_data)
    stmt = """INSERT INTO portfolio_data (key, attr_key, attr_value) 
              VALUES {0};""".format(insert_data_str)
    try:
        cur.execute(stmt)
        conn.commit()
    except Exception as e:
        print('Failed to execute or failed to commit. Statement being executed: {0}'.format(stmt))
        report_db_error(e)
        return
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def main(c, customer_id, p, password, a, account_id, e, email, db_password):
    data = _get_data(c, customer_id, p, password, a, account_id, e, email)

    # Flatten into the structure needed to bulk insert into postgres with psycopg2
    insert_data = []
    for key in data.keys():
        for attr_key in data[key]:
            insert_data.append( (str(key), str(attr_key), str(data[key][attr_key])) )
   
    _store_data(insert_data, db_password)


# Sample call: PROJECT_ROOT$ python ./tests/test_runner_from_cli_examples.py \
#              -c MY_CUSTOMER_ID \
#              -p MY_PASSWORD \
#              -a MY_ACCOUNT_ID \
#              -e MY_EMAIL \
#              -d DB PASSWORD
if __name__ == '__main__':
    import sys

    # Load the module scope variables from CLI args
    # This lets us not hard-code sensitive values needed for the test
    c, customer_id, p, password, a, account_id, e, email, d, db_password = sys.argv[1:]
    
    main(c, customer_id, p, password, a, account_id, e, email, db_password)

