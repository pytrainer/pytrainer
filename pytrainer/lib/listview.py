import datetime
from sqlalchemy import and_
from pytrainer.lib.localization import gtk_str
from pytrainer.lib.uc import UC
from pytrainer.core.activity import Activity

UC_LISTDISTANCE = {False : [[_('All Distances'), [0.0,999999.9]],
                            ['<1 km', [0.0, 1.0]],
                            ['1-5 km', [1.0, 5.0]],
                            ['5-20 km', [5.0, 20.0]],
                            ['20-50 km', [20.0, 50.0]],
                            ['50-100 km', [50.0, 100.0]],
                            ['>100 km', [100.0, 999999.9]]]  ,
                    True : [[_('All Distances'), [0.0,999999.9]],
                            ['<1 mi', [0.0, 1.609344]],
                            ['1-5 mi', [1.609344, 8.04672]],
                            ['5-10 mi', [8.04672, 16.09344]],
                            ['10-20 mi', [16.09344, 32.18688]],
                            ['20-50 mi', [32.18688, 80.4672]],
                            ['>50 mi', [80.4672, 999999.9]]] 
                    }
class ListSearch(object):
    """ Builds SQLite condition out of search parameters"""
    def __init__(self, sport_service, parent=None):
        self.parent = parent    
        self.uc = UC()
        """ Initialize all query parameters to valid default values""" 
        self.title = ''
        self.sport = 0
        self.past = 0
        self.duration = 0
        self.distance = 0        
        self.listSport = sport_service.get_all_sports()
        
        self.listPast = [[_('All Time'), -99999], [_('Last 4 Weeks'), -31],
                         [_('Last 6 Months'), -183], [_('Last 12 Months'), -366]]
                         
        self.listDuration = [[_('All Durations'), [0,999999]],
                             [_('<1 Hour'), [0,3600]],
                             [_('1-2 Hours'), [3600,7200]],
                             [_('>2 Hours'), [7200,999999]]]
       
        """
        self.listDistanceUS = [['All Distances', [0.0,999999.9]],
                             ['<1 mi', [0.0, 1.609344]],
                             ['1-5 mi', [1.609344, 8.04672]],
                             ['5-10 mi', [8.04672, 16.09344]],
                             ['10-20 mi', [16.09344, 32.18688]],
                             ['20-50 mi', [32.18688, 80.4672]],
                             ['>50 mi', [80.4672, 999999.9]]]        
                                                            
        self.listDistance = [['All Distances', [0.0,999999.9]],
                             ['<1 km', [0.0, 1.0]],
                             ['1-5 km', [1.0, 5.0]],
                             ['5-20 km', [5.0, 20.0]],
                             ['20-50 km', [20.0, 50.0]],
                             ['50-100 km', [50.0, 100.0]],
                             ['>100 km', [100.0, 999999.9]]]
        """
        
        self.listDistance = UC_LISTDISTANCE[self.uc.us]
        #print self.listDistance           
        self.setup_lsa_sport()
        self.setup_lsa_past()
        self.setup_lsa_duration()
        self.setup_lsa_distance()

    def get_condition(self):
        """ Assembles an sqlalchemy query object """
        _andlist = []
        if self.title:
            _andlist.append(Activity.title.like('%' + self.title + '%'))
        if self.sport:
            _andlist.append(Activity.sport == self.listSport[self.sport-1])
        if self.listPast[self.past][1]:
            _delta = datetime.timedelta(days=self.listPast[self.past][1])
            _date = datetime.datetime.today() + _delta
            _andlist.append(Activity.date > _date)
        if self.listDuration[self.duration][1]:
            _dur_min = int(self.listDuration[self.duration][1][0])
            _dur_max = int(self.listDuration[self.duration][1][1])
            _andlist.append(Activity.duration.between(_dur_min, _dur_max))
        if self.listDistance[self.distance][1]:
            _dis_min = int(self.listDistance[self.distance][1][0])
            _dis_max = int(self.listDistance[self.distance][1][1])
            _andlist.append(Activity.distance.between(_dis_min, _dis_max))
        ret = None
        first = True
        for expr in _andlist:
            if first:
                ret = expr
                first = False
            else:
                ret = and_(ret, expr)
        return ret

    """    
    def get_listDistance(self):
        
        _all = ['All Distances', [0.0, 99999.9]]
        _back = []
        _back.append( [_all] )
        for sp in self.listSport:
            _back.append( [_all] )
        return _back    
    """
        
    condition = property(get_condition)
    #listDuration = property(get_listDuration)
    
    def setup_lsa_sport(self):
        liststore_lsa =  self.parent.lsa_sport.get_model() 
        if self.parent.lsa_sport.get_active() != 0:
            self.parent.lsa_sport.set_active(0) #Set first item active if isnt
        firstEntry = gtk_str(self.parent.lsa_sport.get_active_text())
        liststore_lsa.clear() #Delete all items
        #Re-add "All Sports"
        liststore_lsa.append([firstEntry])
        #Re-add all sports in listSport
        for sport in self.listSport:
            liststore_lsa.append([sport.name])
        self.parent.lsa_sport.set_active(0)
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_sport.connect("changed", self.parent.on_listareasearch_clicked)

    def setup_lsa_past(self):
        liststore_lsa =  self.parent.lsa_past.get_model() 
        if self.parent.lsa_past.get_active() > 0:
            self.parent.lsa_past.set_active(0) #Set first item active isnt
        firstEntry = gtk_str(self.parent.lsa_past.get_active_text())
        liststore_lsa.clear() #Delete all items
        for i in self.listPast:
            liststore_lsa.append([i[0]])
        self.parent.lsa_past.set_active(0)    
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_past.connect("changed", self.parent.on_listareasearch_clicked)
        
    def setup_lsa_duration(self):
        liststore_lsa =  self.parent.lsa_duration.get_model() 
        if self.parent.lsa_duration.get_active() > 0:
            self.parent.lsa_duration.set_active(0) 
        firstEntry = gtk_str(self.parent.lsa_duration.get_active_text())
        liststore_lsa.clear() #Delete all items        
        for i in self.listDuration:
            liststore_lsa.append([i[0]])
        self.parent.lsa_duration.set_active(0)
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_duration.connect("changed", self.parent.on_listareasearch_clicked)        
        
    def setup_lsa_distance(self):
        liststore_lsa =  self.parent.lsa_distance.get_model() 
        if self.parent.lsa_distance.get_active() > 0:
            self.parent.lsa_distance.set_active(0) 
        firstEntry = gtk_str(self.parent.lsa_distance.get_active_text())
        liststore_lsa.clear() #Delete all items        
        for i in self.listDistance:
            liststore_lsa.append([i[0]])
        self.parent.lsa_distance.set_active(0)  
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_distance.connect("changed", self.parent.on_listareasearch_clicked)             

    def reset_lsa(self):
        """ Reset all query parameters to default values """
        self.title = ''
        self.sport = 0
        self.past = 0
        self.duration = 0
        self.distance = 0   
        self.parent.lsa_searchvalue.set_text('')
        self.parent.lsa_sport.set_active(0)  
        self.parent.lsa_past.set_active(0)        
        self.parent.lsa_duration.set_active(0)
        self.parent.lsa_distance.set_active(0)
 
