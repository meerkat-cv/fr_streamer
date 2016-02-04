from enum import IntEnum
import statistics

class CoherenceMethod(IntEnum):
    hard_threshold = 1
    score_mean = 2
    score_median = 3


class TempCoherence():

    def __init__(self, temp_window, method, threshold):
        self.last_pos = 0
        self.temp_window = temp_window
        self.past = temp_window/2 + 1

        self.labels = [[] for k in range(self.temp_window)]
        self.costs = [[] for k in range(self.temp_window)]

        self.method = method
        self.threshold = threshold


    def hard_threshold_method(self):
        labels_count = {}
        people_count = {}
        persons = []

        for i in range(0,self.temp_window):
            curr_labels = self.labels[i]

            for j in range(0,len(curr_labels)):
                if self.costs[i][j] > self.threshold:
                    if labels_count.get(curr_labels[j]) is None:
                        labels_count[curr_labels[j]] = 1
                    else:
                        labels_count[curr_labels[j]] = labels_count[curr_labels[j]] + 1
            
            if people_count.get(len(curr_labels)) is None:
                people_count[len(curr_labels)] = 1
            else:
                people_count[len(curr_labels)] = people_count[len(curr_labels)] + 1
        

        num_people = 0
        for p_c in people_count:
            num_people = num_people + p_c

        for labels_key in labels_count.keys():
            num_labels = labels_count[labels_key]
            if num_labels > self.past and len(persons) < num_people:
                persons.append(labels_key)
        
        return persons


    def score_method(self):
        labels_costs = {}
        persons = []
        
        for i,curr_labels in enumerate(self.labels):
            for j,label in enumerate(curr_labels):
                if len(labels_costs) == 0:
                    labels_costs[label] = [ self.costs[i][j] ]
                else:
                    labels_costs[label].append(self.costs[i][j])

        for label in labels_costs.keys():
            score = self.calc_score(labels_costs[label])
            if score > self.threshold:
                persons.append(label)

        return persons


    def calc_score(self, costs_vec):
        if self.method == CoherenceMethod.score_mean:
            return statistics.mean(costs_vec)

        if self.method == CoherenceMethod.score_median:
            return statistics.median(costs_vec)

        print('Undefined TempCoherence method.')

        return 0.5


    def add_frame(self, ores, min_confidence):
        (self.labels[self.last_pos], self.costs[self.last_pos]) = self.extract_info(ores)
        self.last_pos = (self.last_pos+1) % self.temp_window;

        if self.method == CoherenceMethod.hard_threshold:
            return self.format_response( self.hard_threshold_method() )
        else:
            return self.format_response( self.score_method() )
        


    def format_response(self, persons):
        detections = []
        for p in persons:
            d = {}
            d = {'recognition': {'predictedLabel': p}}
            detections.append(d)

        res = {'people': detections}

        return res


    def extract_info(self, ores):
        labels = []
        costs = []

        for people in ores['people']:
            labels.append(people['recognition']['predictedLabel'])
            costs.append(people['recognition']['confidence'])

        return (labels, costs)

