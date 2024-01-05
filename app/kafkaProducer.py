from kafka import KafkaConsumer, KafkaProducer
import kafka
import ssl
import logging

# logging.basicConfig(level=logging.DEBUG)

try:
    topic = "sendMessage"
    sasl_mechanism = "PLAIN"
    username = "test"
    password = "testtest"
    security_protocol = "SASL_SSL"

    # context = ssl.create_default_context()
    # context.options &= ssl.OP_NO_TLSv1
    # context.options &= ssl.OP_NO_TLSv1_1

    consumer = KafkaConsumer('handshake-py', bootstrap_servers='localhost:9094',
                             # api_version=(0, 10),

                             security_protocol=security_protocol,
                             group_id='my_favorite_group',
                             # ssl_context=context,
                             ssl_check_hostname=False,
                             ssl_cafile='./testHelpers/certs/ca.pem',
                             ssl_certfile='./testHelpers/certs/ca.crt',
                             ssl_keyfile='./testHelpers/certs/ca.key',
                             ssl_password='confluents',
                             sasl_mechanism=sasl_mechanism,
                             sasl_plain_username=username,
                             sasl_plain_password=password)


    # ssl_certfile='../keys/certificate.pem',
    # ssl_keyfile='../keys/key.pem')#,api_version = (0, 10))

    producer = KafkaProducer(bootstrap_servers='localhost:9094',
                             # api_version=(0, 10),
                             security_protocol=security_protocol,
                             # ssl_context=context,
                             ssl_check_hostname=False,
                             ssl_cafile='./testHelpers/certs/ca.pem',
                             ssl_certfile='./testHelpers/certs/ca.crt',
                             ssl_keyfile='./testHelpers/certs/ca.key',
                             ssl_password='confluents',
                             sasl_mechanism=sasl_mechanism,
                             sasl_plain_username=username,
                             sasl_plain_password=password)
    # ssl_certfile='../keys/certificate.pem',
    # ssl_keyfile='../keys/key.pem')#, api_version = (0,10))
    # Write hello world to test topic
    # for _ in range(100):
    #     producer.send(topic, b'some_message_bytes')
    print("Consumer and Producer instances created successfully!")
    future = producer.send(topic, b'Hello from python')
    result = future.get(timeout=6000)
    producer.flush()
    print("Message sent successfully!")

    for msg in consumer:
        print(msg)


except Exception as e:
    print(e)
