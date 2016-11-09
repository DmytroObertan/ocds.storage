from ..backends.couch import TendersStorage, ReleasesStorage
from ocds.storage.backends.fs import FSStorage
import os
from ocds.export.release import get_release_from_tender, do_releases
from ocds.storage.models import ReleaseDoc


class MainStorage(object):

    def __init__(self, config, basepath):
        self.rel_storage = ReleasesStorage(config.get("releases_db"))
        self.ten_storage = TendersStorage(config.get("tenders_db"))
        self.fs_storage = FSStorage(basepath)
        self.info = config.get('release')
        self.basepath = basepath

    def _find(self, ocid):
        for res in self.rel_storage.get_ocid(ocid):
            if res:
                return True
            else:
                return False

    def __contains__(self, key):
        self._find(key)

    def get_releases_for_record(self):
        for doc in self.rel_storage.get_finished_ocids():
            same_ocids = []
            release = doc[0]
            is_same = doc[1]
            if is_same:
                same_ocids.append(release)
            else:
                same_ocids.append(release)
                releases = same_ocids
                same_ocids = []
                yield releases

    def is_finished(self, status):
        if status in ['complete', 'unsuccesful', 'cancelled']:
            return True
        else:
            return False

    def form_doc(self, ocid, path, status, _id):
        return ReleaseDoc(_id=_id,
                          path=path,
                          ocid=ocid,
                          finished=self.is_finished(status)
                          ).__dict__['_data']

    def _write(self):
        for ten in self.ten_storage:
            if ten:
                ten = ten[:-1]
            for release in do_releases(ten, self.info['prefix']):
                _id = release['id']
                self.fs_storage.save(release)
                path = os.path.join(
                    self.basepath, self.fs_storage._path_from_date(release['date']))
                self.rel_storage.save(self.form_doc(release['ocid'],
                                                    path,
                                                    release['tender']['status'],
                                                    _id)
                                      )

    def save(self):
        self._write()
