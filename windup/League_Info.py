# -*- coding: utf-8 -*-
class leagueFormation:
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
