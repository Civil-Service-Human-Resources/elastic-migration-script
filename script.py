from datetime import datetime
import creds
import datetime
import json

from elastic import ElasticClient


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = f"{DATE_FORMAT}T{TIME_FORMAT}:%S"

COURSE_CLASS="uk.gov.cslearning.catalogue.domain.Course"
ELEARNINGMODULE_CLASS="uk.gov.cslearning.catalogue.domain.module.ELearningModule"
LINKMODULE_CLASS="uk.gov.cslearning.catalogue.domain.module.LinkModule"
FACETOFACEMODULE_CLASS="uk.gov.cslearning.catalogue.domain.module.FaceToFaceModule"
FILEMODULE_CLASS="uk.gov.cslearning.catalogue.domain.module.FileModule"
VIDEOMODULE_CLASS="uk.gov.cslearning.catalogue.domain.module.VideoModule"

module_class_map = {
    "face-to-face": FACETOFACEMODULE_CLASS,
    "link": LINKMODULE_CLASS,
    "video": VIDEOMODULE_CLASS,
    "file": FILEMODULE_CLASS,
    "elearning": ELEARNINGMODULE_CLASS
}

class FileWorker:

    def __init__(self) -> None:
        pass

    def write_json_file(file_name, json_content):
        with open(file_name, "w") as file:
            file.write(json.dumps(json_content))

class JobInterface:

    def __init__(self, existing_client: ElasticClient,
                new_client: ElasticClient, file_worker: FileWorker) -> None:
        self.existing_client = existing_client
        self.new_client = new_client
        self.file_worker = file_worker

    def _get_index(self) -> str:
        pass
    
    def _format_data(self, object) -> object:
        pass

    def run(self):
        index = self._get_index()
        existing_data = self.existing_client.get_all_docs(index)
        failed_docs = []
        successful_docs = []
        print(f"processing {existing_data['total']} {index} documents")
        for course in existing_data['content']:
            try:
                source = course['_source']
                formatted_data = self._format_data(source)
                self.new_client.insert_doc(index, formatted_data, formatted_data['id'])
                successful_docs.append(source)
            except Exception as e:
                print(f"{index} document failed: {e}")
                failed_docs.append(source)
        
        if (failed_docs):
            self.file_worker.write_json_file(f"failed_{index}.json", failed_docs)
            print(f"{len(failed_docs)} {index} documents failed")

        with open(f"migrated_{index}.json", "w") as file:
            self.file_worker.write_json_file(f"migrated_{index}.json", successful_docs)
            print(f"{len(successful_docs)} {index} documents succeeded")

class MediaJob(JobInterface):

    def _get_index(self):
        return "media"

    def _format_data(self, media):
        # dateAdded
        # Remove ms as they're not stored as decimals here, which causes the 
        # conversion to fail
        media['dateAdded'].pop()
        media['dateAdded'] = datetime.datetime(*media['dateAdded']).strftime(DATETIME_FORMAT)
        return media

class CourseJob(JobInterface):

    def _get_index(self):
        return "courses"
    
    def _format_date_range(self, date_range):
        date_range['date'] = datetime.datetime(*date_range['date']).strftime(DATE_FORMAT)
        date_range['startTime'] = datetime.time(*date_range['startTime']).strftime(TIME_FORMAT)
        date_range['endTime'] = datetime.time(*date_range['endTime']).strftime(TIME_FORMAT)
        return date_range

    def _format_module_type(self, module_type):
        module_class = module_class_map.get(module_type)
        if not module_class:
            raise Exception(f"module type {module_type} not recognised")

        return module_class

    def _format_data(self, course):
        # audiences requiredBy time
        for audience in course['audiences']:
            if audience['requiredBy']:
                audience['requiredBy'] = datetime.datetime.fromtimestamp(audience['requiredBy']).strftime(DATETIME_FORMAT)

        for module in course['modules']:
            if module['type'] == "face-to-face":
                for event in module['events']:
                    # check for event date ranges - some old modules
                    # do not include them but they are required.
                    if event.get('dateRanges'):
                        event['dateRanges'] = [self._format_date_range(date_range) for date_range in event['dateRanges']]
                    else:
                        raise Exception("Event module does not have dateRanges")
            
            # Some old modules don't have a valid URL, which causes the frontend to fail.
            # Check for URLs for content that requires a URL.
            if module['type'] in ["video", "elearning", "link", "file"] and not module['url']:
                raise Exception(f"module is a {module['type']} module but does not have a URL")

            # ! moduleType is derived from the springboot data elasticsearch package,
            # so remove it to avoid any errors. _class is required as it is added by
            # Elastic on insert.
            module['_class'] = self._format_module_type(module['type'])
            del module['moduleType']

        course['_class'] = COURSE_CLASS

        return course

def run():
    existing_client = ElasticClient(
        creds.existing_elastic_repo_endpoint,
        creds.existing_elastic_repo_username,
        creds.existing_elastic_repo_password
    )

    new_client = ElasticClient(
        creds.new_elastic_repo_endpoint,
        creds.new_elastic_repo_username,
        creds.new_elastic_repo_password
    )
    course_job = CourseJob(existing_client, new_client)
    media_job = MediaJob(existing_client, new_client)

    course_job.run()
    media_job.run()