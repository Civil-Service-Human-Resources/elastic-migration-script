import json
import unittest
from unittest.mock import MagicMock
from script import CourseJob, FileWorker, MediaJob, LearningProviderJob, FileWorker

from elastic import ElasticClient

class Tests(unittest.TestCase):

    def get_elastic_client(self):
        return ElasticClient("", "", "")

    def load_sample_data_resp(self, data_key):
        with open(f"test_files/existing_{data_key}_response.json", "r") as file:
            course = json.loads(file.read())
            return {"total": 1, "content": [course]}

    def get_module(self, course, module_id):
        return [mod for mod in course['modules'] if mod['id'] == module_id][0]

    def test_course_job(self):
        course_resp = self.load_sample_data_resp("course")
        existing_client = self.get_elastic_client()
        existing_client.get_all_docs = MagicMock(return_value=course_resp)

        new_client = self.get_elastic_client()
        new_client.insert_doc = MagicMock()

        file_worker = FileWorker()
        file_worker.write_json_file = MagicMock()
        
        test_job = CourseJob(existing_client, new_client, file_worker)
        test_job.run()

        file_worker_args = file_worker.write_json_file.call_args.args
        successful_docs = file_worker_args[1]
        self.assertEqual(len(successful_docs), 1)

        call_args = new_client.insert_doc.call_args.args

        index = call_args[0]
        formatted_course = call_args[1]
        _id = call_args[2]

        self.assertEqual(index, "courses")

        self.assertEqual(_id, "courseID")

        self.assertEqual(formatted_course['audiences'][0]['requiredBy'], "2022-01-01T00:00:00")
        self.assertEqual(formatted_course['_class'], "uk.gov.cslearning.catalogue.domain.Course")

        f2f_module = self.get_module(formatted_course, "mod-f2f")
        self.assertEqual(f2f_module['_class'], "uk.gov.cslearning.catalogue.domain.module.FaceToFaceModule")

        link_module = self.get_module(formatted_course, "mod-link")
        self.assertEqual(link_module['_class'], "uk.gov.cslearning.catalogue.domain.module.LinkModule")

        file_module = self.get_module(formatted_course, "mod-file")
        self.assertEqual(file_module['_class'], "uk.gov.cslearning.catalogue.domain.module.FileModule")

        video_module = self.get_module(formatted_course, "mod-video")
        self.assertEqual(video_module['_class'], "uk.gov.cslearning.catalogue.domain.module.VideoModule")

        elearning_module = self.get_module(formatted_course, "mod-elearning")
        self.assertEqual(elearning_module['_class'], "uk.gov.cslearning.catalogue.domain.module.ELearningModule")

        date_ranges = f2f_module['events'][0]['dateRanges']
        self.assertEqual(date_ranges[0]['date'], "2022-01-01")
        self.assertEqual(date_ranges[0]['startTime'], "00:00")
        self.assertEqual(date_ranges[0]['endTime'], "00:00")
        self.assertEqual(date_ranges[1]['date'], "2022-02-01")
        self.assertEqual(date_ranges[1]['startTime'], "06:00")
        self.assertEqual(date_ranges[1]['endTime'], "07:00")


    def test_media_job(self):
        media_resp = self.load_sample_data_resp("media")
        existing_client = self.get_elastic_client()
        existing_client.get_all_docs = MagicMock(return_value=media_resp)

        new_client = self.get_elastic_client()
        new_client.insert_doc = MagicMock()

        file_worker = FileWorker()
        file_worker.write_json_file = MagicMock()
        
        test_job = MediaJob(existing_client, new_client, file_worker)
        test_job.run()

        file_worker_args = file_worker.write_json_file.call_args.args
        successful_docs = file_worker_args[1]
        self.assertEqual(len(successful_docs), 1)

        insert_doc_call_args = new_client.insert_doc.call_args.args
        index = insert_doc_call_args[0]
        formatted_media = insert_doc_call_args[1]
        _id = insert_doc_call_args[2]

        self.assertEqual(index, "media")
        self.assertEqual(_id, "mediaID")
        self.assertEqual(formatted_media['dateAdded'], "2022-01-01T01:00:00")


    def test_learning_provider_job(self):
        learning_provider_resp = self.load_sample_data_resp("learning_provider")
        existing_client = self.get_elastic_client()
        existing_client.get_all_docs = MagicMock(return_value=learning_provider_resp)

        new_client = self.get_elastic_client()
        new_client.insert_doc = MagicMock()

        file_worker = FileWorker()
        file_worker.write_json_file = MagicMock()
        
        test_job = LearningProviderJob(existing_client, new_client, file_worker)
        test_job.run()

        file_worker_args = file_worker.write_json_file.call_args.args
        successful_docs = file_worker_args[1]
        self.assertEqual(len(successful_docs), 1)

        insert_doc_call_args = new_client.insert_doc.call_args.args
        index = insert_doc_call_args[0]
        learning_provider = insert_doc_call_args[1]
        _id = insert_doc_call_args[2]

        self.assertEqual(index, "lpg-learning-providers")
        self.assertEqual(_id, "learningProviderID")
        self.assertEqual(learning_provider['name'], "learning-provider")


unittest.main()

