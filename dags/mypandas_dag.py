from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator

args = {
    'owner': 'pipis',
    'start_date': days_ago(1)
}
 
dag = DAG(dag_id = 'my_pandas_dag', default_args=args, schedule_interval=None)
base_datapath = '/opt/airflow/data'

 
def exec_model():
    import pandas as pd
    import statsmodels.api as sm
    from sklearn.metrics import r2_score
    from sklearn.model_selection import train_test_split

    data = pd.read_csv(f'{base_datapath}/mussel.csv')

    X = data[['AREA']].copy()
    Y = data['SPECIES']

    X['AREA2'] = X['AREA'] ** 2
    X['AREA3'] = X['AREA'] ** 3

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33)

    X_train = sm.add_constant(X_train) # adding a constant
    X_test = sm.add_constant(X_test) # adding a constant

    model = sm.OLS(Y_train, X_train).fit(normalize=True)
    Y_train_pred = model.predict(X_train)
    Y_test_pred = model.predict(X_test)

    print("R2 model on training data: %f" % r2_score(Y_train, Y_train_pred))
    print("R2 model on test data: %f" % r2_score(Y_test, Y_test_pred))

    import matplotlib.pyplot as plt

    # Plot the result by building an expression for the fitting function
    x = np.linspace(data['AREA'].min(), data['AREA'].max(), 100)
    yhat = model.params['const'] + model.params['AREA'] * x + model.params['AREA2'] * (x**2) + model.params['AREA3'] * (x**3)
    plt.plot(x, yhat, lw=2, c='orange')

    plt.scatter(data['AREA'], data['SPECIES'], color='green')
    plt.grid(True)
    plt.savefig('/tmp/regression.png')

    return {
        'R2 model on training data': r2_score(Y_train, Y_train_pred),
        'R2 model on test data': r2_score(Y_test, Y_test_pred)
    }
 
with dag:
    create_table = PostgresOperator(
        task_id = "make_a_staging_table",
        postgres_conn_id = "my_pg_connection",
        sql = """CREATE TABLE IF NOT EXISTS regression_results
        (
            test_id SERIAL PRIMARY KEY,
            file_name TEXT,
            image BYTEA
        );
            """
        )
    
    regression = PythonOperator(
        task_id='regression',
        python_callable = exec_model
    )

    store_file = None
 
    create_table >> regression >> store_file