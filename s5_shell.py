import os
import subprocess
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

            awsAccessKeyId = config['default']['aws_access_key_id']
            awsSecretAccessKey = config['default']['aws_secret_access_key']

            self.s3Client = boto3.client('s3', aws_access_key_id=awsAccessKeyId, aws_secret_access_key=awsSecretAccessKey)

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
            elif command.startswith('locs3cp'):
                self.copyLocalToCloud(command)
            else:
                self.executeLocalCommand(command)

    def createBucket(self, command):
        _, bucketName = command.split()
        print(f"Creating bucket: {bucketName}")

    def changeLocation(self, command):
        _, newLocation = command.split()
        self.currentLocation = newLocation
        print(f"Changing location to: {newLocation}")
        print(f"S5{self.currentLocation}>", end=" ")

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

        except Exception as e:
            print(f"Cannot list contents of this S3 location. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")

    def copyLocalToCloud(self, command):
        try:
            _, localFilePath, s3Destination = command.split()

            if not os.path.isfile(localFilePath):
                raise FileNotFoundError(f"Local file '{localFilePath}' not found.")

            bucketName, s3ObjectKey = s3Destination.split('/', 1)

            self.s3Client.upload_file(localFilePath, bucketName, s3ObjectKey)

            print(f"Successfully copied '{localFilePath}' to '{s3Destination}'")
            print(f"S5{self.currentLocation}>", end=" ")

        except Exception as e:
            print(f"Unsuccessful copy. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")

    def executeLocalCommand(self, command):
        # Use -r flag for directories
        nonCloudCommands = ['cd', 'ls', 'pwd', 'echo', 'mkdir', 'rm', 'mv', 'cp', 'cat']

        if any(command.startswith(cmd) for cmd in nonCloudCommands):
            self.executeLocalShellCommand(command)
        else:
            # For any other commands, pass to the session's shell
            os.system(command)

    def executeLocalShellCommand(self, command):
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"S5{self.currentLocation}>", end=" ")
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute command. Error: {e}")
            print(f"S5{self.currentLocation}>", end=" ")

if __name__ == "__main__":
    s5Shell = S5Shell()
