import os
import configparser
import boto3

class S5Shell:
    def __init__(self):
        self.s3Client = None
        self.currentLocation = '/'
        self.connectToAWS()
        self.runShell()

    def connectToAWS(self):
        try:
            config = configparser.ConfigParser()
            config.read('S5-S3.conf')

            aws_access_key_id = config['default']['aws_access_key_id']
            aws_secret_access_key = config['default']['aws_secret_access_key']

            self.s3Client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            self.printWelcomeMessage(success=True)
        except Exception as e:
            self.printWelcomeMessage(success=False, errorMessage=str(e))

    def printWelcomeMessage(self, success, errorMessage=None):
        if success:
            print("Welcome to the AWS S3 Storage Shell (S5)")
            print("You are now connected to your S3 storage")
            print(f"S5{self.currentLocation}>", end=" ")
        else:
            print("Welcome to the AWS S3 Storage Shell (S5)")
            print("You could not be connected to your S3 storage")
            if errorMessage:
                print(f"Error: {errorMessage}")
            print("Please review procedures for authenticating your account on AWS S3")

    def runShell(self):
        while True:
            command = input()

            if command.lower() in ['quit', 'exit']:
                break
            elif command.startswith('create_bucket'):
                self.createBucket(command)
            elif command.startswith('chlocn'):
                self.changeLocation(command)
            elif command.startswith('list'):
                self.listContents(command)
            else:
                self.executeLocalCommand(command)

    def createBucket(self, command):
        # Placeholder for createBucket functionality
        _, bucketName = command.split()
        print(f"Creating bucket: {bucketName}")

    def changeLocation(self, command):
        # Placeholder for changeLocation functionality
        _, newLocation = command.split()
        print(f"Changing location to: {newLocation}")

    def listContents(self, command):
        # Placeholder for listContents functionality
        _, s3Location = command.split()
        print(f"Listing contents of: {s3Location}")

    def executeLocalCommand(self, command):
        # Placeholder for executing local commands
        os.system(command)

if __name__ == "__main__":
    s5Shell = S5Shell()
