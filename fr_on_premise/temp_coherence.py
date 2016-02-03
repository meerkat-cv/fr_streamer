class TempCoherence():

    def __init__(self, temp_window):
        self.last_pos = 0
        self.temp_window = temp_window
        self.past = temp_window/2 + 1

        self.labels = [[] for k in range(self.temp_window)]
        self.costs = [[] for k in range(self.temp_window)]


    def add_frame(self, ores, min_confidence):
        persons = [];
        (self.labels[self.last_pos], self.costs[self.last_pos]) = self.extract_info(ores)
        self.last_pos = (self.last_pos+1) % self.temp_window;

        labels_count = {}
        people_count = {}

        for i in range(0,self.temp_window):
            curr_labels = self.labels[i]

            for j in range(0,len(curr_labels)):
                if self.costs[i][j] > min_confidence:
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
        
        return self.format_response(persons)


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

