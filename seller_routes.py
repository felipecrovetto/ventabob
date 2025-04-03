from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_login import login_required, current_user
from . import db
from .forms import SellProductForm
from .models import Product, Sale
from io import StringIO
import csv

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

@seller_bp.before_request
@login_required
def seller_required():
    if current_user.role != 'seller':
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('index'))

@seller_bp.route('/sell', methods=['GET', 'POST'])
def sell():
    form = SellProductForm()
    if request.method == 'POST':
        sale_data = request.form.get('sale_data')
        payment_method = request.form.get('payment_method')

        if sale_data:
            try:
                sale_items = json.loads(sale_data)
                for item in sale_items:
                    product = Product.query.get(item['id'])
                    if product and product.stock >= item['quantity']:
                        sale_price = product.price * item['quantity']
                        new_sale = Sale(product_id=product.id, seller_id=current_user.id, quantity=item['quantity'], sale_price=sale_price, payment_method=payment_method)
                        db.session.add(new_sale)
                        product.stock -= item['quantity']
                    elif not product:
                        flash(f"El producto con ID {item['id']} no existe.", 'danger')
                        db.session.rollback()
                        return redirect(url_for('seller.sell'))
                    else:
                        flash(f"No hay suficiente stock para {product.name}.", 'danger')
                        db.session.rollback()
                        return redirect(url_for('seller.sell'))
                db.session.commit()
                flash('Venta registrada exitosamente.', 'success')
                return redirect(url_for('seller.sell'))
            except json.JSONDecodeError:
                flash('Error al procesar los datos de la venta.', 'danger')
            except Exception as e:
                flash(f'Ocurrió un error al registrar la venta: {e}', 'danger')
                db.session.rollback()
        else:
            flash('No se agregaron productos a la venta.', 'warning')

    all_products = Product.query.all()
    return render_template('seller/sell.html', form=form, all_products=all_products)

@seller_bp.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('seller/products.html', products=products)

@seller_bp.route('/download_products')
@login_required
def download_seller_products():
    products = Product.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Nombre del Producto', 'Código', 'Precio de Venta', 'Costo', 'Stock'])
    for product in products:
        cw.writerow([product.name, product.code, product.price, product.cost, product.stock])
    output = si.getvalue().encode('utf-8')
    si.seek(0)
    return send_file(si, mimetype='text/csv', as_attachment=True, download_name='productos.csv')

@seller_bp.route('/search_products')
@login_required
def search_products():
    query = request.args.get('query')
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
        results = [{'id': p.id, 'name': p.name, 'price': float(p.price)} for p in products]
        return jsonify(results)
    return jsonify([])

import json