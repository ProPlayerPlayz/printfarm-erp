from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/materials')
def materials():
    # Mock data for materials
    # ideally this comes from DB "Filament" table but we want pretty images
    # We can fetch filaments from DB and map them to images or just hardcode for the gallery as requested "simple page".
    # User said "simple page showing images for the different color filaments offered".
    # Let's show categories.
    
    materials_data = {
        'PLA': [
            {'color': 'Black', 'image': 'spool_black.png'},
            {'color': 'White', 'image': 'spool_white.png'},
            {'color': 'Blue', 'image': 'spool_blue.png'},
            {'color': 'Red', 'image': 'spool_red.png'}
        ],
        'PETG': [
            {'color': 'Black', 'image': 'spool_black.png'},
            {'color': 'Grey', 'image': 'spool_white.png'}, # Placeholder reuse
            {'color': 'Orange', 'image': 'spool_red.png'} # Placeholder reuse
        ],
        'ABS': [
            {'color': 'Black', 'image': 'spool_black.png'},
             {'color': 'Natural', 'image': 'spool_white.png'} # Placeholder reuse
        ]
    }
    return render_template('main/materials.html', materials=materials_data)

@main_bp.route('/gallery')
def gallery():
    return render_template('main/gallery.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')
