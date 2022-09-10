def deploy_app() -> None:
    from app import app, db
    from flask_migrate import upgrade, migrate, init, stamp
    
    app.app_context().push()
    
    db.create_all()
    try:
        init()
    except:
        pass
    stamp()
    migrate()
    upgrade()

def clear_db() -> None:
    from app import app, db
    from app import models
    db.drop_all()
    db.create_all()
    user = models.User(
        username='admin',
        password='paasword',
        name='Admin',
        age=99,
    )
    print("===================\nCleaned DB\n")
    db.session.add(user)
    db.session.commit()
    print("===================\nAdded user Admin\n")

def run_server(host: str, port: int) -> None:
    from app import app
    if host == None:
        host = '0.0.0.0'
    if port == None:
        port = 5000
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Run this server", epilog="Have Fun")
    server_group = parser.add_argument_group("Flask Application")
    server_group.add_argument("-runserver", default=False, action="store_true", help='Run Flask Application with default host and port, Can Change in -host and -port')
    server_group.add_argument("-host", type=str, default="0.0.0.0", help='Change the host ip of Flask Server, To Access it on other PC\'s, Use 0.0.0.0')
    server_group.add_argument("-port", type=int, default=5000, help="Enter the Port Manually")
    db_group = parser.add_argument_group('Database Functions')
    db_group.add_argument("-deploy", default=False, action="store_true", help="It initializes the db models in the models.py file.... stamps it, migrates it, and upgrades it")
    db_group.add_argument('-cleardb', default=False, action="store_true", help="Clears the DB")
    
    args = parser.parse_args()
    if args.runserver:
        run_server(host=args.host, port=args.port)
    if args.deploy:
        deploy_app()
    if args.cleardb:
        clear_db()
    
