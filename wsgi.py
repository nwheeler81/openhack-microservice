from flask import Flask
from flask import abort
from flask import make_response
import json
from flask import request
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
from cassandra import ConsistencyLevel
import os

application = Flask(__name__)

db = os.environ.get('CASSANDRA_HOST', '127.0.0.1')

print "Connecting to database"
raitings = []
cluster = Cluster([db])
session = cluster.connect()

@application.errorhandler(404)
def not_found(error):
    return make_response(json.dumps({'error': 'not found'}), 404)

@application.route('/raitings/api/v1.0/shops/send',methods=['POST'])
def create_raiting():
    if not request.json or not 'raiting_by_user' in request.json:
        abort(400)
    raiting = {
       'product_name':request.json['product_name'],
       'raiting_by_user':request.json['raiting_by_user'], 
       'price':request.json['price'],
       'store_id':request.json['store_id']
      }
    insert_raiting(request.json['store_id'],request.json['product_name'],request.json['price'],request.json['raiting_by_user'])
    return json.dumps({'raiting': raiting}), 201

@application.route('/receipts/api/v1.0/shops/send',methods=['POST'])
def create_receipts():
    if not request.json:
        abort(400)
    receipts = {
       'topic':request.json['topic'],
       'value':request.json['value'],
       'store_id':request.json['store_id']
      }    
    insert_receipts(request.json['topic'],
                request.json['value'],
                request.json['store_id'])
    return json.dumps({'receipts': receipts}), 201

@application.route('/raitings/api/v1.0/shops/<int:shop_id>', methods=['GET'])
def get_raitings(shop_id):
    pass
#    raiting = [shop for shop in shops if shop['shop_id'] == shop_id] 
#    if len(raiting) == 0:
#        abort(404)
#    return json.dumps({'result':raiting[0]})

def insert_raiting(store_id, product_name, price, raiting):
    query = session.prepare("INSERT INTO shop_raitings.raitings_by_shop_id(store_id, product_name,price,raiting,ts) VALUES (?, ? ,?, ?, dateof(now()))")
    batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
    batch.add(query,(store_id, product_name, float(price), raiting))
    session.execute(batch)

def insert_receipts(topic, value, store_id):
    query = session.prepare("INSERT INTO shop_receipts.receipts_by_store_id(topic, value, store_id, ts) VALUES (? ,?, ?, dateof(now()))")
    batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
    batch.add(query,(topic,float(value), store_id))
    session.execute(batch)


def index():
    return "Working"

if __name__=='__main__':
    application.run(debug=False)
