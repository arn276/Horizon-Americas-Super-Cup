import itertools


class leagueFormation:
    def teamLsts(leageDict):
        conferenceTms,divisionTms, groupTms = [],[],[]
        leagueFormat = []
        for conf in leageDict.keys(): 
            confLst = []
            # confPairings.append([conf])
            for div in leageDict[conf].keys():
                divLst = []
                for grp in leageDict[conf][div].keys():
                    groupLst = list(leageDict[conf][div][grp].keys())
                    groupTms.append(groupLst)
                    divLst.append(groupLst)
                    leagueFormat.append([conf,div,grp,groupLst])
                divisionTms.append(leagueFormation.flattenLsts(divLst))
                confLst.append(leagueFormation.flattenLsts(divLst))
            conferenceTms.append(leagueFormation.flattenLsts(confLst))
        # self.leagueLsts = [leagueFormat,conferenceTms,divisionTms,groupTms]
        
        return leagueFormat, conferenceTms, divisionTms, groupTms
        
    
    def flattenLsts(lst):
        return list(itertools.chain.from_iterable(lst))
    
    
    def leagueDict():
        leagueConferences = {
            'Founders': {'East Division':{'Port Group':{'Montreal':{'Nickname':'Fantômes'},
                                                       'Boston':{'Nickname':'Nexus'},
                                                       'New Haven':{'Nickname':'Melon Heads'},
                                                       'New York':{'Nickname':'Gators'}
                                                       },
                                          'Canal Group':{'Philadelphia':{'Nickname':'Apes'},
                                                       'Pittsburgh':{'Nickname':'Pack'},
                                                       'Toronto':{'Nickname':'Monsters'},
                                                       'Washington, D.C.':{'Nickname':'Patrol'}
                                                        }
                                         },
                         'West Division':{
                                          'Aurora Group':{'Winnipeg':{'Nickname':'Irratiate'},
                                                          'St. Paul':{'Nickname':'Enigmas'},
                                                          'Chicago':{'Nickname':'Pledge'},
                                                          'St. Louis':{'Nickname':'Hornets'}
                                                         },
                                          'Rail Group':{'Detroit':{'Nickname':'Rouge'},
                                                        'Indianapolis':{'Nickname':'Beasts'},
                                                        'Akron':{'Nickname':'Haz'},
                                                        'Columbus':{'Nickname':'Spark'}
                                                       }
                                         }
                        },
            'Visionaries': {'East Division':{'Ridge Group':{'Nashville':{'Nickname':'Scream'},
                                                            'Charlotte':{'Nickname':'Cats'},
                                                            'Atlanta':{'Nickname':'Liz'},
                                                            'Birmingham':{'Nickname':'Howl'}
                                                            },
                                             'Desert Group':{'Dallas':{'Nickname':'Vampires'},
                                                            'San Antonio':{'Nickname':'Bears'},
                                                            'Monterrey':{'Nickname':'Owls'},
                                                            'Merida':{'Nickname':'Jaguars'}
                                                             }
                                         },
                            'West Division':{'Pass Group':{'Calgary':{'Nickname':'Wendigos'},
                                                             'Vancouver':{'Nickname':'Lizards'},
                                                             'Denver':{'Nickname':'Tommynockers'},
                                                             'Seattle':{'Nickname':'Bats'}
                                                             },
                                             'Rush Group':{'Oakland':{'Nickname':'Phantoms'},
                                                           'Los Angeles':{'Nickname':'Hex'},
                                                           'Phoenix':{'Nickname':'Cult of the Atom'},
                                                           'Tijuana':{'Nickname':'Visitors'}
                                                          }
                                            }
                           }
        }
        return leagueConferences
