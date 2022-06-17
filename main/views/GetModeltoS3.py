import os
import boto3
import sys


class GetModeltoS3:
    def downloadModel(self):
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get("ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("SECRET_KEY"),
        )

        def download(s3_bucket, s3_object_key, local_file_name):
            meta_data = s3.head_object(Bucket=s3_bucket, Key=s3_object_key)
            total_length = int(meta_data.get('ContentLength', 0))
            downloaded = 0
            def progress(chunk):
                nonlocal downloaded
                downloaded += chunk
                done = int(50 * downloaded / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                sys.stdout.flush()

            print(f'Downloading {s3_object_key}')
            with open(local_file_name, 'wb') as f:
                s3.download_fileobj(s3_bucket, s3_object_key, f, Callback=progress)
            print()

        model = './BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar'
        word = './WORDMAP_coco_5_cap_per_img_5_min_word_freq.json'
        bucket="seear"

        if not os.path.isfile(model):
            download(bucket, 'BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar', model)
        if not os.path.isfile(word):
            s3.download_file(bucket, 'WORDMAP_coco_5_cap_per_img_5_min_word_freq.json', word)