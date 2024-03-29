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

    # Prints a welcome message based on the success of connecting to AWS S3.
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

    # Connects to AWS S3 using the credentials from the configuration file.
    def connectToAWS(self):
        try:
            config = configparser.ConfigParser()
            config.read('S5-S3.conf')

            aws_access_key_id = config['default']['aws_access_key_id']
            aws_secret_access_key = config['default']['aws_secret_access_key']

            self.s3Client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            self.s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

            self.printWelcomeMessage(success=True)
            return 0
        except Exception as e:
            self.printWelcomeMessage(success=False, error_message=str(e))
            return 1
        
    # Copies files from a local directory to an S3 bucket.
    def copyLocalToCloud(self, command):
        try:
            _, localFolderPath, s3Destination = command.split()

            if not os.path.isdir(localFolderPath):
                raise FileNotFoundError(f"Local folder '{localFolderPath}' not found.")

            if not localFolderPath.endswith('/'):
                localFolderPath += '/'

            bucket_name, s3_prefix = s3Destination.split('/', 1)

            if localFolderPath.startswith('/'):
                localFolderPath = localFolderPath[1:]
                s3_prefix = os.path.join(s3_prefix, os.path.basename(localFolderPath))

            for root, _, files in os.walk(localFolderPath):
                for file in files:
                    localFilePath = os.path.join(root, file)
                    s3ObjectKey = os.path.join(s3_prefix, os.path.relpath(localFilePath, localFolderPath))

                    self.s3Client.upload_file(localFilePath, bucket_name, s3ObjectKey)

            print(f"Successfully copied '{localFolderPath}' to '{s3Destination}'")
            print(f"S5{self.currentLocation}>", end=" ")
            return 0
        except Exception as e:
            print(f"Unsuccessful copy. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 1

    # Executes a shell command locally.
    def executeLocalShellCommand(self, command):
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"S5{self.currentLocation}>", end=" ")
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute command. Error: {e}")
            print(f"S5{self.currentLocation}>", end=" ")

    # Executes a local command, handling both cloud and non-cloud commands.
    def executeLocalCommand(self, command):
        # Use -r flag for directories
        nonCloudCommands = ['cd', 'ls', 'pwd', 'echo', 'mkdir', 'rm', 'mv', 'cp', 'cat']

        if any(command.startswith(cmd) for cmd in nonCloudCommands):
            self.executeLocalShellCommand(command)
        else:
            os.system(command)

    # Creates a new S3 bucket.
    def createBucket(self, command):
        try:
            _, bucketName = command.split()
            
            if not bucketName[1:].islower() or not all(char.isalnum() or char in ['-', '.'] for char in bucketName[1:]):
                raise ValueError("Invalid bucket name. Bucket names must consist only of lowercase letters, numbers, hyphens, and periods.")
            
            if not bucketName.startswith('/'):
                raise ValueError("Invalid bucket name format. Bucket names must start with '/'.")

            existing_buckets = [bucket['Name'].lower() for bucket in self.s3Client.list_buckets().get('Buckets', [])]
            if bucketName[1:].lower() in existing_buckets:
                raise ValueError("Bucket with the same name already exists. Please choose a different name.")

            self.s3Client.create_bucket(Bucket=bucketName[1:], CreateBucketConfiguration={'LocationConstraint': 'ca-central-1'})
            print(f"Successfully created bucket: {bucketName}")

            print(f"S5{self.currentLocation}>", end=" ")
            return 0 
        except Exception as e:
            print(f"Cannot create bucket. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 1
        
    # Extracts the bucket name and directory path from the current location.
    def get_bucket_and_directory(self):
        parts = self.currentLocation.strip('/').split('/')
        if len(parts) == 1:
            return parts[0], ''
        else:
            return parts[0], '/'.join(parts[1:])

    # Changes the current location in the S3 space.
    def changeLocation(self, command):
        try:
            _, newLocation = command.split()

            if newLocation == '..':
                parts = self.currentLocation.strip('/').split('/')
                if len(parts) > 1:
                    self.currentLocation = '/'.join(parts[:-1])
                else:
                    self.currentLocation = '/'
            elif newLocation == '../..':
                parts = self.currentLocation.strip('/').split('/')
                if len(parts) > 2:
                    self.currentLocation = '/'.join(parts[:-2])
                else:
                    self.currentLocation = '/'
            elif newLocation == '/':
                self.currentLocation = '/'
            else:
                if not newLocation.startswith('/'):
                    raise ValueError("Invalid location format. Location must start with '/'.")

                self.currentLocation = newLocation

            print(f"Changing location to: {self.currentLocation}")

            bucket_name, directory_path = self.get_bucket_and_directory()
            bucket = self.s3_resource.Bucket(bucket_name)

            for obj in bucket.objects.filter(Prefix=directory_path):
                if obj.key == directory_path:
                    print(f"S5{self.currentLocation}>", end=" ")
                    return 0
                else:
                    print(f"Cannot change folder. Error: Directory does not exist.")
                    return 1

            print(f"S5{self.currentLocation}>", end=" ")
            return 0

        except Exception as e:
            print(f"Cannot change folder. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 1

    # Displays the current working location in the S3 space.
    def currentWorkingLocation(self):
        try:
            if self.currentLocation == '/':
                print("/")
                print(f"S5{self.currentLocation}>", end=" ")
                return 0
            else:
                print(f"{self.currentLocation[1:]}:{self.currentLocation}")
                print(f"S5{self.currentLocation}>", end=" ")
                return 0

        except Exception as e:
            print(f"Cannot access location in S3 space. Error: {str(e)}")
            print(f"S5{self.currentLocation}>", end=" ")
            return 1

    # Lists the contents of an S3 location specified in the command.
    def listContents(self, command):
        try:
            _, s3Location = command.split()

            if s3Location == '/':
                response = self.s3Client.list_buckets()
                buckets = [bucket['Name'] for bucket in response['Buckets']]

                if not buckets:
                    print("No buckets found in the root directory.")
                else:
                    print("\n".join(buckets))
            else:
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

    # Enters a loop to accept and process user commands until the user decides to quit.
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
            elif command.startswith('cwlocn'):
                self.currentWorkingLocation()
            else:
                self.executeLocalCommand(command)

if __name__ == "__main__":
    s5Shell = S5Shell()
