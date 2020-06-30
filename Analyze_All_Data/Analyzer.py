import json
import pandas as pd
import matplotlib.pyplot as plt
import sys
import re
from os import path

sys.path.append("../")
sys.path.append("./")

class Analyzer:
    def __init__(self):
        # self.filename = 'all_data.csv'
        # if path.exists(self.filename):
        #     self.df = pd.read_csv(self.filename)
        # else:
        self.df = pd.DataFrame(columns=('date', 'cam_id', 'night', 'dense', 'type', 'place', 'vehicle_count', 'pedestrian_count'))

    def merge(self, dict1, dict2):
        return (dict2.update(dict1))

    def load_json(self, json_file):
        with open(json_file, 'r') as infile:
            d = json.load(infile)
        return d

    def consolidate_individual_video_detections(self, filenames):
        """
        if all video detections separate, first merge into one dictionary
        :param filenames: list of filenames
        :return: merged dict {cam_id: {date: {frame:count, frame: count}}, cam_id:...}
        """
        with open (filenames[0], 'r') as file:
            merged_dict = json.load(file)

        for each in filenames[1:]:
            with open (each, 'r') as file:
                d = json.load(file)
                print(d.keys())
                print(len(d.keys()))
                self.merge(merged_dict, d)

        print(merged_dict.keys())
        print(len(merged_dict.keys()))
        return merged_dict

    def simplify_video_detections(self, video_dict: dict, filename):
        """
        function to parse video detections to max_video detections (same format as image detections)

        input: {cam_id: {date: {frame:count, frame: count}}}
        :return: simplified dict {cam_id: {date: count, date: count}}
        """
        simplified_dict = dict()
        for cam_id in video_dict:
            simplified_dict[cam_id] = dict()

            for date_time in video_dict[cam_id]:
                max_count = 0
                for frame in video_dict[cam_id][date_time]:
                    count = 0
                    for detection in video_dict[cam_id][date_time][frame]:
                        if float(detection) > 0.3:
                            count += 1
                    if count > max_count:
                        max_count = count
                simplified_dict[cam_id][date_time] = max_count

        with open(filename, 'w+') as simple_fp:
            simple_fp.write(json.dumps(simplified_dict))

        return simplified_dict

    def normalize_simplified_dict(self, in_dict):
        d = in_dict.copy()
        print(d)

        for cam_id in d.keys():
            try:
                largest_value = max(d[cam_id].values())
            except ValueError:
                largest_value = float('inf')

            for date in d[cam_id]:
                d[cam_id][date] = d[cam_id][date]/largest_value
        return d


    def add_results_df(self, results_dict, cam_type, object):
        """
        function to parse simplified json results into dataframe
        if video data, results must be simplified first using simplify_video_detections

        results_dict = either a video or image dictionary of results
        cam_type = ['video', 'image']
        object = ['vehicle', 'person']
        :return: None
        """
        for cam_id in results_dict:
            for date_time in results_dict[cam_id]:
                print('date_time', date_time)
                p = re.compile('\d\d\d\d-\d\d-\d\d')
                data = dict()
                data = {'date': pd.to_datetime(p.search(date_time).group(0)), 'cam_id': cam_id, 'type': cam_type}

                if object == 'vehicle':
                    data['vehicle_count'] = results_dict[cam_id][date_time]
                elif object == 'person':
                    data['pedestrian_count'] = results_dict[cam_id][date_time]

                self.df = self.df.append(data, ignore_index=True, sort=False)

        self.df.to_csv('all_data.csv')
        print(self.df)

    def plot_time_series(self):
        """
        @Todo: plot time series of each unique cam
        :return: graph
        """
        pass

    def easy_plot(self, video_simple_results):

        for key in video_simple_results.keys():
            l = []
            for each in video_simple_results[key]:
                l.append(video_simple_results[key][each])
            plt.plot(l, label=key)
            plt.legend()

        plt.show()

    def plot_car_detections(self, filename):

        with open(filename, 'r') as detections:
            d = json.load(detections)

        print(len(d.keys()))
        all_counts = dict()

        for cam_id in d.keys():
            print('cam_id', cam_id)
            counts = dict()
            for image_name in d[cam_id]:
                counts[image_name] = 0
                for detection in d[cam_id][image_name]:
                    # if float(detection) > 0.3:
                    counts[image_name] += 1
            all_counts[cam_id] = counts

        self.easy_plot(all_counts)

if __name__ == "__main__":

    """
    example usage
    """

    a = Analyzer()


    """
    plot person detections from raw video results
    """
    # # save raw results into one dict
    # video_results_files = ['../person_detections_video']
    # merged_dict = a.consolidate_individual_video_detections(video_results_files)

    # # simplify raw dict
    # simple_video_results = a.simplify_video_detections(merged_dict, 'simple_video_detections_person')

    # # normalize
    # simple_video_results_normalized = a.normalize_simplified_dict(simple_video_results)

    # # plot
    # a.easy_plot(simple_video_results_normalized)


    """
    add json detections into dataframe
    """

    # simple_video_results_person = a.load_json('simple_video_detections_person')
    # a.add_results_df(simple_video_results_person, 'video', 'person')
    #
    # image_results_car = a.load_json('../vehicle_detections.json')
    # image_results_car_simple = a.simplify_video_detections(image_results_car, 'simple_image_detections_car')
    # a.add_results_df(image_results_car_simple, 'image', 'vehicle')

    image_results_people = a.load_json('../person_detections.json')
    image_results_people_simple = a.simplify_video_detections(image_results_people, 'simple_image_detections_people')
    a.add_results_df(image_results_people_simple, 'image', 'person')






