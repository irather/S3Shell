import configparser
import boto3

class S5Shell:
    def __init__(self):
        self.s3Client = None
        self.connectToAWS()

    def connectToAWS(self):
        try:
            config = configparser.ConfigParser()
            config.read('S5-S3.conf')

            aws_access_key_id = config['default']['aws_access_key_id']
            aws_secret_access_key = config['default']['aws_secret_access_key']

            self.s3Client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            self.printWelcomeMessage(success = True)
        except Exception as e:
            self.printWelcomeMessage(success = False, errorMessage = str(e))

    def printWelcomeMessage(self, success, errorMessage = None):
        if success:
            print("Welcome to the AWS S3 Storage Shell (S5)")
            print("You are now connected to your S3 storage")
        else:
            print("Welcome to the AWS S3 Storage Shell (S5)")
            print("You could not be connected to your S3 storage")
            if errorMessage:
                print(f"Error: {error_message}")
            print("Please review procedures for authenticating your account on AWS S3")

if __name__ == "__main__":
    s5_shell = S5Shell()
