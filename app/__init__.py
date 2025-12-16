from flask import Flask
from app.config import config
from app.extensions import db, login_manager, migrate, csrf

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.customer.routes import customer_bp
    app.register_blueprint(customer_bp, url_prefix='/customer')

    from app.operator.routes import operator_bp
    app.register_blueprint(operator_bp, url_prefix='/operator')

    from app.ops.routes import ops_bp
    app.register_blueprint(ops_bp, url_prefix='/ops')

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.blueprints.analytics.routes import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/analytics')

    from app.blueprints.main.routes import main_bp
    app.register_blueprint(main_bp, url_prefix='/')
    
    # Root redirect (optional, or handle in nginx)
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('customer.home'))

    return app
