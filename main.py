if __name__ == "__main__":

    import uvicorn
    import argparse
    from app import app
    from app import routes

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port", help="Specify the port to run the webserver on")
    parser.add_argument("-i", "--ip", help="Specify the IP to run the webserver on")

    args = parser.parse_args()

    import socket
    host = socket.gethostbyname(socket.gethostname())
    port = 7000
    if args.port:
        port = int(args.port)
    if args.ip:
        host = str(args.ip)


    uvicorn.run(app, host=host, port=port)
