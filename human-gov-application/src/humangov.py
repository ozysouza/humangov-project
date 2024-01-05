from flask import Flask, redirect, url_for, render_template, request, flash
from forms import RecordForm
import os
import uuid
import boto3
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr


from helpers import upload_file, generate_unique_filename, allowed_file, create_presigned_url

from config import AWS_BUCKET, AWS_REGION, AWS_DYNAMODB_TABLE, US_STATE
# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['DEBUG'] = False


dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(AWS_DYNAMODB_TABLE)

def get_item(id):
    try:
        response = table.get_item(Key={'id': id})
        return response['Item'] if 'Item' in response else None
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None

def get_all_items():
    try:
        response = table.scan()
        return response['Items'] if 'Items' in response else []
    except ClientError as e:
        print(e.response['Error']['Message'])
        return []

def update_item(id, record):
    try:
        table.update_item(
            Key={'id': id},
            UpdateExpression="SET #fn=:first_name, #ln=:last_name, #rl=:role, salary=:salary, pdf=:pdf",
            ExpressionAttributeValues={
                ':first_name': record['first_name'],
                ':last_name': record['last_name'],
                ':role': record['role'],
                ':salary': record['salary'],
                ':pdf': record['pdf']
            },
            ExpressionAttributeNames={
            "#fn": "first_name",
            "#ln": "last_name",
            "#rl": "role"
            },
            ReturnValues="UPDATED_NEW"
        )
        return True
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False


@app.route("/")
def index():
    '''
    Home page
    '''
    return render_template('web/home.html',US_STATE=US_STATE)


@app.route("/new_record", methods=('GET', 'POST'))
def new_record():
    '''
    Create new record
    '''
    form = RecordForm()
    if form.validate_on_submit():
        file_to_upload = request.files['pdf']
        final_file_name = generate_unique_filename(form.first_name.data)
        item_id = str(uuid.uuid4())
        item_first_name = form.first_name.data
        item_last_name = form.last_name.data
        item_role = form.role.data
        item_salary = form.salary.data

        if not file_to_upload:
            flash('File not selected.','danger')
            return render_template('web/new_record.html', form=form)
        
        if file_to_upload and not allowed_file(file_to_upload.filename):
            flash('Invalid file format. Only PDFs allowed.','warning')
            return render_template('web/new_record.html', form=form)

        try:
            filename = secure_filename(file_to_upload.filename)
            file_to_upload.save(filename)
            upload_file(filename,AWS_BUCKET,final_file_name)
            os.remove(filename)
            
            table.put_item(
                Item={
                    'id': item_id,
                    'first_name': item_first_name,
                    'last_name': item_last_name,
                    'role': item_role,
                    'salary': item_salary,
                    'pdf': final_file_name
                }
            )
            # User info
            flash('Record addeed successfully.', 'success')
            return redirect(url_for('records'))
        except Exception as error:
            print(error)
            flash('Error while trying to add record.', 'danger')

    return render_template('web/new_record.html', form=form)


@app.route("/edit_record/<id>", methods=('GET', 'POST'))
def edit_record(id):
    form = RecordForm()
    response = table.get_item(Key={'id': id})
    item = response['Item']

    if form.validate_on_submit():
            table.update_item(
                Key={'id': id},
                UpdateExpression="SET #fn=:first_name, #ln=:last_name, #rl=:role, salary=:salary",
                ExpressionAttributeValues={
                    ':first_name': form.first_name.data,
                    ':last_name': form.last_name.data,
                    ':role': form.role.data,
                    ':salary': form.salary.data
                },
                ExpressionAttributeNames={
                "#fn": "first_name",
                "#ln": "last_name",
                "#rl": "role"
                }
            )
            flash('Record updated successfully.', 'success')
            return redirect(url_for('records'))

    form.first_name.data = item['first_name']
    form.last_name.data = item['last_name']
    form.role.data = item['role']
    form.salary.data = item['salary']

    return render_template('web/edit_record.html', item=item, form=form)


@app.route("/records")
def records():
    '''
    Show all records
    '''
    records = get_all_items()
    sorted_records = sorted(records, key=lambda x: x['first_name'])
    return render_template('web/records.html', records=sorted_records)



@app.route("/search")
def search():
    '''
    Search
    '''
    name_search = request.args.get('name')

    if not name_search:
        name_search = ""

    response = table.scan(
        FilterExpression=Attr('first_name').contains(name_search)
    )
    all_records = response.get('Items', [])

    return render_template('web/records.html', records=all_records)


@app.route("/records/delete", methods=('POST',))
def records_delete():
    '''
    Delete record
    '''
    record_id = request.form['id']

    try:
        table.delete_item(Key={'id': record_id})
        flash('Deleted successfully.', 'danger')
    except ClientError as e:
        print(e.response['Error']['Message'])
        flash('Error while deleting.', 'danger')

    return redirect(url_for('records'))

@app.route("/records/pdf/<id>", methods=('GET',))
def records_pdf(id):
    '''
    View signed form

    :param id: Id from pdf
    '''
    my_record = get_item(id)
    if my_record:
        pdf_form_pre_signed_url = create_presigned_url(AWS_BUCKET, my_record['pdf'])
        return redirect(pdf_form_pre_signed_url)
    else:
        flash('Error: Record not found.', 'danger')
        return redirect(url_for('records'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
