from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from .forms import AddProductForm, AddStockForm
from .models import Product, Sale
from . import db
from io import StringIO
import csv
import pandas as pd
from sqlalchemy import extract
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('index'))

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    add_product_form = AddProductForm()
    add_stock_form = AddStockForm()
    all_products = Product.query.all()

    if add_product_form.validate_on_submit():
        code = add_product_form.code.data
        name = add_product_form.name.data
        price = add_product_form.price.data
        cost = add_product_form.cost.data
        stock = add_product_form.stock.data
        new_product = Product(code=code, name=name, price=price, cost=cost, stock=stock)
        db.session.add(new_product)
        db.session.commit()
        flash(f'Producto "{name}" agregado exitosamente.', 'success')
        return redirect(url_for('admin.add_product'))

    return render_template('admin/add_product.html', form=add_product_form, stock_form=add_stock_form, all_products=all_products)

@admin_bp.route('/add_stock', methods=['POST'])
def add_stock():
    stock_form = AddStockForm()
    if stock_form.validate_on_submit():
        product_code = stock_form.existing_product_code.data
        add_stock_quantity = request.form.get('add_stock_quantity', type=int)
        product = Product.query.filter_by(code=product_code).first()
        if product and add_stock_quantity is not None and add_stock_quantity > 0:
            product.stock += add_stock_quantity
            db.session.commit()
            flash(f'Se agregaron {add_stock_quantity} unidades al stock de "{product.name}".', 'success')
            return redirect(url_for('admin.add_product'))
        else:
            flash('Código de producto no válido o cantidad de stock no válida.', 'danger')
    return redirect(url_for('admin.add_product'))

@admin_bp.route('/product_list')
def product_list():
    products = Product.query.all()
    product_data = [{'name': product.name, 'stock': product.stock} for product in products]
    product_names = [data['name'] for data in product_data]
    product_stocks = [data['stock'] for data in product_data]
    return render_template('admin/product_list.html', products=products,
                           product_names_json=json.dumps(product_names),
                           product_stocks_json=json.dumps(product_stocks))

@admin_bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddProductForm(obj=product)  # Pre-llenar el formulario con los datos del producto
    if form.validate_on_submit():
        product.code = form.code.data
        product.name = form.name.data
        product.price = form.price.data
        product.cost = form.cost.data
        product.stock = form.stock.data
        db.session.commit()
        flash(f'Producto "{product.name}" actualizado exitosamente.', 'success')
        return redirect(url_for('admin.product_list'))
    return render_template('admin/edit_product.html', form=form, product=product)

@admin_bp.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Producto "{product.name}" eliminado exitosamente.', 'success')
    return redirect(url_for('admin.product_list'))

@admin_bp.route('/download_products')
def download_products():
    products = Product.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Código', 'Nombre del Producto', 'Precio de Venta', 'Costo', 'Stock'])
    for product in products:
        cw.writerow([product.code, product.name, float(product.price), float(product.cost), product.stock])
    output = si.getvalue().encode('utf-8')
    si.seek(0)
    return send_file(si, mimetype='text/csv', as_attachment=True, download_name='productos.csv')

@admin_bp.route('/sales_report')
def sales_report():
    sales = Sale.query.all()
    sales_with_products = []
    for sale in sales:
        product = Product.query.get(sale.product_id)
        sales_with_products.append({
            'sale_id': sale.id,
            'sale_date': sale.sale_date,
            'product_code': product.code if product else 'N/A',
            'product_name': product.name if product else 'Producto no encontrado',
            'quantity': sale.quantity,
            'sale_price': float(sale.sale_price),  # Convert to float
            'cost': float(product.cost) if product else 'N/A',  # Convert to float
            'payment_method': sale.payment_method,
            'seller_id': sale.seller_id
        })

    monthly_sales_objects = db.session.query(
        extract('year', Sale.sale_date).label('year'),
        extract('month', Sale.sale_date).label('month'),
        db.func.sum(Sale.sale_price).label('total_sales')
    ).group_by('year', 'month').order_by('year', 'month').all()

    monthly_sales = []
    for item in monthly_sales_objects:
        monthly_sales.append({
            'year': item.year,
            'month': item.month,
            'total_sales': float(item.total_sales) if item.total_sales else 0.0
        })

    return render_template('admin/sales_report.html', sales=sales_with_products, monthly_sales=monthly_sales)

@admin_bp.route('/download_sales_report')
def download_sales_report():
    sales = Sale.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Fecha de Venta', 'Código de Producto', 'Nombre del Producto', 'Cantidad', 'Precio de Venta', 'Costo', 'Método de Pago'])
    for sale in sales:
        product = Product.query.get(sale.product_id)
        if product:
            cw.writerow([
                sale.sale_date,
                product.code,
                product.name,
                sale.quantity,
                float(sale.sale_price),  # Convert to float
                float(product.cost),  # Convert to float
                sale.payment_method
            ])
        else:
            cw.writerow([
                sale.sale_date,
                'Producto no encontrado',
                'Producto no encontrado',
                sale.quantity,
                float(sale.sale_price),  # Convert to float
                'N/A',
                sale.payment_method
            ])
    output = si.getvalue().encode('utf-8')
    si.seek(0)
    return send_file(si, mimetype='text/csv', as_attachment=True, download_name='reporte_de_ventas.csv')


@admin_bp.route('/sales_charts')
def sales_charts():
    # Datos para el gráfico de ventas por tiempo
    all_sales = Sale.query.all()
    sales_data_for_time = [{'date': sale.sale_date.strftime('%Y-%m-%d'), 'quantity': sale.quantity, 'sale_price': float(sale.sale_price)} for sale in all_sales]
    years = sorted(list(set([sale['date'][:4] for sale in sales_data_for_time])))

    # Datos para el gráfico de inventario por producto
    products = Product.query.all()
    inventory_data = [{'name': product.name, 'stock': product.stock} for product in products]

    # Datos para el gráfico de pastel de cantidad vendida por producto
    sales_by_product = db.session.query(Product.name, db.func.sum(Sale.quantity).label('total_sold')).join(Sale).group_by(Product.name).all()
    labels_sold = [item.name for item in sales_by_product]
    data_sold = [int(item.total_sold) for item in sales_by_product] # Convert to int

    # Datos para el gráfico de pastel de utilidad por producto
    utility_by_product = db.session.query(Product.name, db.func.sum(Sale.sale_price - Product.cost * Sale.quantity).label('total_profit')).join(Sale).group_by(Product.name).all()
    labels_profit = [item.name for item in utility_by_product]
    data_profit = [float(item.total_profit) for item in utility_by_product] # Convert to float

    return render_template('admin/sales_charts.html',
                           sales_data_time=json.dumps(sales_data_for_time),
                           inventory_data=json.dumps(inventory_data),
                           labels_sold=json.dumps(labels_sold),
                           data_sold=json.dumps(data_sold),
                           labels_profit=json.dumps(labels_profit),
                           data_profit=json.dumps(data_profit),
                           years=json.dumps(years))