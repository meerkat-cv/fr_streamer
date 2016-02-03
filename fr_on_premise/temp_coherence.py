class TempCoherence():

    def __init__(self, temp_window):
        self.last_pos = 0
        self.temp_window = temp_window
        self.past = temp_window/2 + 1

        self.labels = [[] for k in range(self.temp_window)]
        costs = [[] for k in range(self.temp_window)]


    def add_frame(ores):
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
        

        # num_people = 0
        # for(auto it=people_count.begin(); it != people_count.end(); it++) {
        #     if(it->second > past_ && it->first > num_people)
        #         num_people = it->first;
        # }
        # if(num_people == 0)
        #     return persons;

        # for(auto it = labels_count.begin(); it != labels_count.end(); it++) {
        #     if(it->second > past_ && persons.size() < num_people) {
        #         persons.push_back(it->first);
        #     }
        # }

        # persons.resize(num_people, 0);

        return self.format_response(persons)


    def format_response(persons):
        detections = []
        for p in persons:
            d['recognition'] = p

        res = {'people', detections}

        return res


    def extract_info(self, ores):
        labels = []
        costs = []

        for people in ores['people']:
            labels.append(ores['recognition']['predictedLabel'])
            costs.append(ores['recognition']['confidence'])

        return (labels, costs)

