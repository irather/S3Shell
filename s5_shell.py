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
            # Read AWS credentials from configuration file
            config = configparser.ConfigParser()
            config.read('S5-S3.conf')

            aws_access_key_id = config['default']['aws_access_key_id']
            aws_secret_access_key = config['default']['aws_secret_access_key']

            # Establish connection to AWS S3
            self.s3Client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

            # Connection successful, display welcome message
            return 0
        except Exception as e:
            # Connection unsuccessful, display error message
            return 1

    def printWelcomeMessage(self, success, errorMessage=None):
        if success:
            print("Welcome to the AWS S3 Storage Shell (S5)")
            print("You are now connected to your S3 storage")
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
        _, bucketName = command.split()
        print(f"Creating bucket: {bucketName}")

    def changeLocation(self, command):
        try:
            _, newLocation = command.split()
            self.currentLocation = newLocation
            print(f"Changing location to: {newLocation}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 0
        except Exception as e:
            print(f"Cannot change location. Error: {str(e)}")
            return 1

    def listContents(self, command):
        try:
            _, s3Location = command.split()

            if s3Location == '/':
                # List buckets if the specified location is '/'
                response = self.s3Client.list_buckets()
                buckets = [bucket['Name'] for bucket in response['Buckets']]

                if not buckets:
                    print("No buckets found in the root directory.")
                else:
                    print("\n".join(buckets))
            else:
                # List objects in the specified S3 location
                response = self.s3Client.list_objects(Bucket=s3Location[1:], Delimiter='/')

                if 'Contents' in response:
                    contents = [obj['Key'] for obj in response['Contents']]
                    print("\n".join(contents))
                else:
                    print(f"No objects found in '{s3Location}'")

            print(f"S5{self.currentLocation}>", end=" ")
            return 0

        except Exception as e:
            print(f"Cannot list contents of this S3 location. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 1

    def executeLocalCommand(self, command):
        try:
            # Placeholder for executing local commands
            os.system(command)
            return 0
        except Exception as e:
            print(f"Error executing local command. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 1

if __name__ == "__main__":
    s5Shell = S5Shell()
