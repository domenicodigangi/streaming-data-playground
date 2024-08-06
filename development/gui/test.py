from confluent_kafka import Consumer

conf = {'bootstrap.servers': 'localhost:29092',
        'group.id': 'foo',
        'enable.auto.commit': 'false',
        'auto.offset.reset': 'earliest'}

consumer = Consumer(conf)

running = True

def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            msg
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False