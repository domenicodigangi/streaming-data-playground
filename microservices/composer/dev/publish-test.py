from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')

# Send two messages to the 'test' topic
producer.send('topic-01', key=b'key', value=b'value1')
producer.send('topic-01', key=b'key', value=b'value2')

producer.flush()
producer.close()
