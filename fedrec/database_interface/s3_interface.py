import os
from abstract_db_interface import AbstractDatabaseManager
import boto3
from fedrec.utilities.error_handler import errorhandler
import pandas as pd

#TODO: Add Asynchronization. Wrappers Needed.


class S3Interface(AbstractDatabaseManager):

    @errorhandler
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
        self.current_buckets = None
        try:

            self.current_buckets = [bucket.name for bucket in self.s3.buckets.all()]
        
        except Exception as e:
            print(e)
        
        print(self.current_buckets)
        pass



    @errorhandler
    def listAllBuckets(self):
        if self.current_buckets == None:
            raise Exception("Info not available.")

        for b in self.current_buckets:
            print(b)

    # def check_bucket_exists(self, bucket_name):
    #     """
    #         Check If The Bucket For Specific Group Exists in Database
    #     """

    #     try:
    #         waiter = self.s3.get_waiter('bucket_exists')
    #         waiter.wait(Bucket=bucket_name,
    #                     WaiterConfig={
    #                         'Delay':2, 'MaxAttempts':3
    #                     })
            
    #         if bucket_name == None:
    #             return False
    #         else:
    #             return True

    #     except Exception as e:
    #         raise Exception("Unexpected error occured in s3.")
    #         return False


    #This function is not working yet. 
    # def create_bucket(self, bucket_name):
    #     """
    #         creates new bucket in s3 database
    #         To be called only after successfully connecting to database

    #     """
    #     try:
    #         res = self.s3.create_bucket(
    #             Bucket=bucket_name,
    #             CreateBucketConfiguration={
    #                 'LocationConstraint': 'ap-south-1',
    #             },
    #         )
    #         if res['ResponseMetadata']['HTTPStatusCode'] == 200:
    #             self.current_buckets = self.s3.buckets.all()
    #             return True
        
    #         else:
    #             return False
    #     except Exception as e:
    #         print(e)
    

    @errorhandler
    def read_data(self, data_id):
        """

        """
        #condition to check if s3 is connected
        if self.current_buckets == None : 
            raise Exception("Error connecting to database.")
        
        #Extract Group of device and model we need to fetch
        bucket = data_id[0]
        model_path =  data_id[1]
        if not bucket in self.current_buckets:
            raise Exception("Requested bucket does not exist.")
        
        data_obj = self.s3.Bucket(bucket).Object(model_path).get()
        body = pd.read_csv(data_obj['Body'], index_col=0)
        
        #process body as required

        return body


    @errorhandler
    def create_data(self, data_id, body):
        if self.current_buckets == None:
            raise Exception("Error connecting to database.")
        
        bucket = data_id[0] #group to which device belongs
        model_path = data_id[1] #path to model

        if not bucket in self.current_buckets:
            #create bucket
            raise Exception("Requested bucket does not exist.")
            # if not self.create_bucket(bucket):
            #     raise Exception("Error creating new device group")
    
        # taking body to be dictionary type (json)
        pd.DataFrame(body).to_csv('foo.csv')
        self.s3.Bucket(bucket).upload_file(Filename='foo.csv', Key=model_path)
        os.remove('foo.csv')


    @errorhandler
    def update_data(self, data_id, new_body):
        if self.current_buckets == None:
            raise Exception("Error connecting to database.")

        # if not self.check_bucket_exists(data_id[0]):
        #     raise Exception("Requested device group does not exist.")

        self.create_data(data_id, new_body)


    @errorhandler
    def delete_data(self, data_id):
        if self.s3 == None:
            raise Exception("Error connecting to database.")
        
        group = data_id[0]
        model_path = data_id[1]

        self.s3.Object(group, model_path).delete()
