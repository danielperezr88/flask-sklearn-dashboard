# -*- coding: UTF-8 -*-
from sys import modules
from glob import glob
from os import path, remove, close, getpid, makedirs
import logging
import shutil
import json
import re

from tempfile import mkstemp
from importlib import reload

from dateutil import parser

from redis import WatchError

from time import sleep

try:
    from google.protobuf import timestamp_pb2
    from gcloud import storage
except BaseException as e:
    pass


default_timestamp = parser.datetime.datetime.fromtimestamp(0)


def save_pid(pname, redis=None, pid=None):

    pid = getpid() if pid is None else pid

    """Prioritarily, save pid on redis db."""
    if redis is not None:
        return redis.set('%s_pid' % (pname,), pid)

    """If none given, save pid into a file: filename.pid."""
    with open("%s.pid" % (pname,), 'w') as fp:
        fp.write(str(pid))


def get_pname(config_key, redis=None, pid=None, pid_as_second_key=False, switch_key_value=False):

    """Prioritarily, get pname from redis db."""
    if redis is not None:
        data = json.loads(redis.get(config_key).decode('latin-1'))

    else:
        with open(config_key, 'r') as fp:
            data = json.loads(fp.read())

    if isinstance(data, dict) and switch_key_value:
        data = {v: k for k, v in data.items()}

    if pid_as_second_key:

        if not isinstance(data, dict):
            return None

        pid = str(getpid() if pid is None else pid)
        return data[pid] if pid in data else None

    return data


def re_sub(pattern, replacement, string):
    def _r(m):
        # Now this is ugly.
        # Python has a "feature" where unmatched groups return None
        # then re.sub chokes on this.
        # see http://bugs.python.org/issue1519638

        # this works around and hooks into the internal of the re module...

        # the match object is replaced with a wrapper that
        # returns "" instead of None for unmatched groups

        class _m():
            def __init__(self, m):
                self.m = m
                self.string = m.string

            def group(self, n):
                return m.group(n) or ""

        return re._expand(pattern, _m(m), replacement)

    return re.sub(pattern, _r, string)


JSON_CONVERTERS = {
    'datetime': parser.parse
}


def metasplit(p, t):
    if t > 0:
        return metasplit(path.split(p)[0], t - 1) + [path.split(p)[1]]
    return list(path.split(p))


class CSEJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (parser.datetime.datetime,)):
            return {"val": obj.isoformat(), "_spec_type": "datetime"}
        #elif isinstance(obj, (decimal.Decimal,)):
        #    return {"val": str(obj), "_spec_type": "decimal"}
        else:
            return super().default(obj)


def cse_json_decoding_hook(obj):
    _spec_type = obj.get('_spec_type')
    if not _spec_type:
        return obj

    if _spec_type in JSON_CONVERTERS:
        return JSON_CONVERTERS[_spec_type](obj['val'])
    else:
        raise Exception('Unknown {}'.format(_spec_type))


def lookup_bucket(cli, prefix=None, suffix=None):
    if suffix is not None or prefix is not None:
        for bucket in cli.list_buckets():
            if suffix is None:
                if bucket.name.startswith(prefix):
                    return bucket.name
            elif prefix is None:
                if bucket.name.endswith(suffix):
                    return bucket.name
            else:
                if bucket.name.startswith(prefix) and bucket.name.endswith(suffix):
                    return bucket.name
        logging.error("Bucket not found")
        return
    logging.error("Any bucket suffix nor prefix specified!")


class BucketedFileRefresher:

    def __init__(self):
        self.timestamps = {}

    def __call__(self, bucket, filename, destination):
        if "google" in modules:

            id_ = "-".join([bucket, filename])

            try:
                client = storage.Client()
                cblob = client.get_bucket(lookup_bucket(client, bucket)).get_blob(filename)
                if (cblob.updated != self.timestamps[id_]) if id_ in self.timestamps else True:
                    self.timestamps.update({id_: cblob.updated})
                    fp = open(destination, 'wb')
                    cblob.download_to_file(fp)
                    fp.close()
            except BaseException as ex:
                msg = "Unable to access file \"%s\": Unreachable or unexistent bucket and file." % (filename,)
                logging.error(msg)
                raise ImportError(msg)


def maybe_populate_client_obj(client_obj=None):

    if client_obj is None:
        if 'google' not in modules:
            return
        else:
            return storage.Client()

    return client_obj


def maybe_upload_file_to_bucket(filename, basename='', client_obj=None, bucket_prefix=None, bucket_suffix=None):

    client_obj = maybe_populate_client_obj(client_obj)
    if client_obj is None:
        return

    bucket_name = lookup_bucket(client_obj, prefix=bucket_prefix, suffix=bucket_suffix)
    if bucket_name is None:
        return

    bucket = client_obj.get_bucket(bucket_name)
    if bucket.get_blob(filename) is None:
        blob = storage.Blob(filename, bucket)
        with open(path.join(basename, filename), 'rb') as fp:
            blob.upload_from_file(fp)

    return client_obj


def remove_old_files_from_bucket(basename='', client_obj=None, bucket_prefix=None, bucket_suffix=None):

    client_obj = maybe_populate_client_obj(client_obj)
    if client_obj is None:
        return

    bucket_name = lookup_bucket(client_obj, prefix=bucket_prefix, suffix=bucket_suffix)
    if bucket_name is None:
        return

    bucket = client_obj.get_bucket(bucket_name)

    blobs = bucket.list_blobs()
    blobs = [b for b in blobs]
    filenames = [path.join(basename, b.name) for b in blobs]
    for filename, blob in zip(filenames, blobs):
        if not path.exists(filename):
            blob.delete()

    return client_obj


def upload_new_files_to_bucket(glob_filename, basename='', client_obj=None, bucket_prefix=None, bucket_suffix=None):

    client_obj = maybe_populate_client_obj(client_obj)
    if client_obj is None:
        return

    bucket_name = lookup_bucket(client_obj, prefix=bucket_prefix, suffix=bucket_suffix)
    if bucket_name is None:
        return

    bucket = client_obj.get_bucket(bucket_name)

    blobs = bucket.list_blobs()
    blob_names = [b.name for b in blobs]
    for filepath in glob(path.join(basename, glob_filename)):
        filename = path.split(filepath)[-1]
        if filename not in blob_names:
            blob = storage.Blob(filename, bucket)
            with open(filepath, 'rb') as fp:
                blob.upload_from_file(fp)

    return client_obj


def maybe_retrieve_entire_bucket(basename='', client_obj=None, bucket_prefix=None, bucket_suffix=None, folder_prefixes=0):

    client_obj = maybe_populate_client_obj(client_obj)
    if client_obj is None:
        return

    bucket_name = lookup_bucket(client_obj, prefix=bucket_prefix, suffix=bucket_suffix)
    if bucket_name is None:
        return

    bucket = client_obj.get_bucket(bucket_name)

    blobs = bucket.list_blobs()
    blobs = [b for b in blobs]
    filenames = [path.join(*(
        [basename] +
        b.name.split('_')[:folder_prefixes] +
        ['_'.join(b.name.split('_')[folder_prefixes:])]
    )) for b in blobs]

    for filename, blob in zip(filenames, blobs):

        filedir = path.split(filename)[0]
        if filedir:
            if not path.exists(filedir):
                makedirs(filedir)

        if not path.exists(filename):
            fp = open(filename, 'wb')
            blob.download_to_file(fp)
            fp.close()

    return client_obj


def update_bucket_status(timestamps, basename='', client_obj=None, bucket_prefix=None, bucket_suffix=None, folder_prefixes=0):

    client_obj = maybe_populate_client_obj(client_obj)
    if client_obj is None:
        return

    bucket_name = lookup_bucket(client_obj, prefix=bucket_prefix, suffix=bucket_suffix)
    if bucket_name is None:
        return

    bucket = client_obj.get_bucket(bucket_name)

    blobs = bucket.list_blobs()
    blobs = [b for b in blobs]
    blob_filenames = [path.join(*(
        [basename] +
        b.name.split('_')[:folder_prefixes] +
        ['_'.join(b.name.split('_')[folder_prefixes:])]
    )) for b in blobs]
    blobs = dict(zip(blob_filenames, blobs))

    for key, timestamp in timestamps.items():
        key_parts = key.split('_')
        n_key_parts = len(key_parts)
        subpath = path.join(
            path.join(*key_parts[:folder_prefixes]) if folder_prefixes != 0 else '',
            '_'.join(key_parts[folder_prefixes:])
        ) + '*'
        for f in glob(path.join(basename, subpath, *(['*']*(folder_prefixes - n_key_parts)))):
            meta = blobs[f].metadata if f in blobs else None
            meta = json.loads(meta['timestamp'], object_hook=cse_json_decoding_hook) if meta is not None else None
            if (meta < timestamp) if meta is not None else True:
                blob = storage.Blob('_'.join(metasplit(f, folder_prefixes)[1:]), bucket)
                with open(f, 'rb') as fp:
                    blob.upload_from_file(fp)
                blob.metadata = dict(timestamp=json.dumps(timestamp, cls=CSEJSONEncoder))
                blob.patch()

    for f, blob in blobs.items():
        if not path.exists(f):
            blob.delete()

    return client_obj


def refresh_and_retrieve_timestamps(redis_client, input_ids, timeframes=[31, 93, 365]):

    with redis_client.pipeline() as pipe:
        while True:
            try:
                pipe.watch('analysis_timestamps')
                timestamps = json.loads(pipe.get('analysis_timestamps').decode('latin-1'),
                                        object_hook=cse_json_decoding_hook)

                any_ = False
                for tf in timeframes:
                    for iid in input_ids:
                        key = "input%d_%dd" % (iid, tf)
                        if key not in timestamps:
                            timestamps[key] = default_timestamp
                            any_ = True

                if any_:
                    pipe.multi()
                    pipe.set('analysis_timestamps', json.dumps(timestamps, cls=CSEJSONEncoder))
                    pipe.execute()

                break

            except WatchError as e:
                sleep(0.5)
                continue

    return timestamps


def create_configfile_or_replace_existing_keys(file_path, patterns):
    fh, abs_path = mkstemp()
    with open(abs_path, 'w', encoding='utf-8') as new_file:
        if not path.exists(file_path):
            try:
                for pline in ["%s = %r\n" % (k, v) for k, v in patterns.items()]:
                    new_file.write(pline)
            except AttributeError as ex:
                print(patterns)
        else:
            with open(file_path) as old_file:
                for line in old_file:
                    changed = False
                    for pname, pline in [(k, "%s = %r\n" % (k, v)) for k, v in patterns.items()]:
                        if list(map(lambda x: x.strip(), line.split('=')))[0] == pname:
                            changed = True
                            new_file.write(pline)
                    if not changed:
                        new_file.write(line)
            remove(file_path)
    close(fh)
    shutil.move(abs_path, file_path)


def refresh_and_retrieve_module(filename, bucketed_file_refresher=None, bucket=None, default=None):

    BFR = BucketedFileRefresher() if bucketed_file_refresher is None else bucketed_file_refresher

    while True:

        try:

            filepath = path.join(path.dirname(path.realpath(__file__)), filename)
            if bucket is not None:
                BFR(bucket, filename, filepath)

            module = __import__(path.splitext(filename)[0])
            return reload(module)

        except BaseException as ex:

            if path.exists(filepath):
                module = __import__(path.splitext(filename)[0])
                return reload(module)

            if default is not None:
                create_configfile_or_replace_existing_keys(filepath, default)
                continue

            msg = "Unable to access file \"%s\": Unreachable or unexistent bucket, file and default." % (filename,)
            logging.error(msg)
            raise ImportError(msg)


"""
url matching regex
http://daringfireball.net/2010/07/improved_regex_for_matching_urls

The regex patterns in this gist are intended to match any URLs,
including "mailto:foo@example.com", "x-whatever://foo", etc. For a
pattern that attempts only to match web URLs (http, https), see:
https://gist.github.com/gruber/8891611
"""
ANY_URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""

"""
The regex patterns in this gist are intended only to match web URLs -- http,
https, and naked domains like "example.com". For a pattern that attempts to
match all URLs, regardless of protocol, see: https://gist.github.com/gruber/249502
"""
WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

