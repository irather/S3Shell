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
            # Read AWS credentials from configuration file
            config = configparser.ConfigParser()
            config.read('S5-S3.conf')

            aws_access_key_id = config['default']['aws_access_key_id']
            aws_secret_access_key = config['default']['aws_secret_access_key']

            # Establish connection to AWS S3
            self.s3Client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

            # Connection successful, display welcome message
            self.printWelcomeMessage(success=True)
            return 0
        except Exception as e:
            # Connection unsuccessful, display error message
            self.printWelcomeMessage(success=False, error_message=str(e))
            return 1

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
        try:
            _, bucketName = command.split()

            # Ensure the bucket name follows S3 naming conventions
            
            if not bucketName[1:].islower() or not all(char.isalnum() or char in ['-', '.'] for char in bucketName[1:]):
                raise ValueError("Invalid bucket name. Bucket names must consist only of lowercase letters, numbers, hyphens, and periods.")
            
            if not bucketName.startswith('/'):
                raise ValueError("Invalid bucket name format. Bucket names must start with '/'.")

            existing_buckets = [bucket['Name'].lower() for bucket in self.s3Client.list_buckets().get('Buckets', [])]
            if bucketName[1:].lower() in existing_buckets:
                raise ValueError("Bucket with the same name already exists. Please choose a different name.")

            # Perform the S3 bucket creation using boto3 with LocationConstraint
            self.s3Client.create_bucket(Bucket=bucketName[1:], CreateBucketConfiguration={'LocationConstraint': 'ca-central-1'})
            print(f"Successfully created bucket: {bucketName}")

            print(f"S5{self.currentLocation}>", end=" ")
            return 0 
        except Exception as e:
            print(f"Cannot create bucket. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 1

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
