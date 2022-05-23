import AbstractDatabaseManager
import boto3
import pandas as pd

class S3Interface(AbstractDatabaseManager):

    def __init__(self,
                region=None,
                aws_access_key=None,
                aws_secret_access_key=None
                ):
        
        self.region = region

        self.s3 = boto3.resource(
                service_name='s3',
                region_name=region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_access_key
        )

        pass


    async def check_bucket_exists(self, bucket_name):
        """
            Check If The Bucket For Specific Group Exists in Database
        """

        try:
            waiter = self.s3.get_waiter('bucket_exists')
            await waiter.wait(Bucket=bucket_name,
                        WaiterConfig={
                            'Delay':2, 'MaxAttempts':3
                        })
            
            if bucket_name == None:
                return False
            else:
                return True

        except Exception as e:
            raise Exception("Unexpected error occured in s3.")
            return False



    async def create_bucket(self, bucket_name):
        """
            creates new bucket in s3 database
            To be called only after successfully connecting to database

        """
        res = await self.s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'Location-Constraint': self.region,
            },
        )
        if res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        
        else:
            return False

    
    async def read_data(self, data_id):
        """

        """
        #condition to check if s3 is connected
        if self.s3 == None : 
            raise Exception("Error connecting to database.")
        
        #Extract Group of device and model we need to fetch
        bucket = data_id[0]
        model_path = data_id[1]

        if ! self.check_bucket_exists(bucket):
            raise Exception("Requested Device Group Does Not Exist.")
        
        data_obj = await self.s3.Bucket(bucket).Object(model_path).get()
        body = pd.read_csv(data_obj['Body'], index_col=0)
        
        #process body as required

        return body


    async def create_data(self, data_id, body):
        if self.s3 == None:
            raise Exception("Error connecting to database.")
        
        bucket = data_id[0] #group to which device belongs
        model_path = data_id[1] #path to model

        if ! self.check_bucket_exists(bucket):
            #create bucket
            if ! self.create_bucket(bucket):
                raise Exception("Error creating new device group")
    
        # taking body to be dictionary type (json)
        foo = pd.DataFrame(body).to_csv('foo.csv')
        await self.s3.Bucket(bucket).upload_file(Filename='foo.csv', Key=model_path)


    async def update_data(self, data_id, new_body):
        if self.s3 == None:
            raise Exception("Error connecting to database.")

        if ! self.check_bucket_exists(data_id[0]):
            raise Exception("Requested device group does not exist.")

        # TODO: look for update function in s3
        self.create_data(data_id, new_body)
    


    async def delete_data(self, data_id):
        if self.s3 == None:
            raise Exception("Error connecting to database.")
        
        group = data_id[0]
        model_path = data_id[1]

        await self.s3.Object(group, model_path).delete()
