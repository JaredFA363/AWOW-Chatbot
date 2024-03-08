import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def fuzzy_wonder_recommendation(historical_significance_score, architectural_beauty_score):
    wonder_names = {
        0: 'Great Wall Of China',
        1: 'City of Petra',
        2: 'Christ the Redeemer',
        3: 'Machu Picchu',
        4: 'Chichen Itza',
        5: 'Roman Colosseum',
        6: 'Taj Mahal',
        7: 'None'
    }
    
    # Fuzzy variables
    historical_significance = ctrl.Antecedent(np.arange(0, 11, 1), 'historical_significance')
    architectural_beauty = ctrl.Antecedent(np.arange(0, 11, 1), 'architectural_beauty')
    wonder_choice = ctrl.Consequent(np.arange(0, 8, 1), 'wonder_choice')  # 8 choices: 0 to 7
    
    # Membership functions
    names = ['low', 'medium', 'high']
    historical_significance.automf(names=names)
    architectural_beauty.automf(names=names)
    wonder_choice.automf(names=['Great Wall', 'Petra', 'Christ the Redeemer', 'Machu Picchu', 'Chichen Itza', 'Colosseum', 'Taj Mahal', 'None'])
    
    # Rules
    rule1 = ctrl.Rule(historical_significance['low'] | architectural_beauty['low'], wonder_choice['None'])
    rule2 = ctrl.Rule(historical_significance['medium'] & architectural_beauty['medium'], wonder_choice['Machu Picchu'])
    rule3 = ctrl.Rule(historical_significance['high'] & architectural_beauty['high'], wonder_choice['Taj Mahal'])
    
    # Create control system
    wonder_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    wonder_recommendation = ctrl.ControlSystemSimulation(wonder_ctrl)
    
    wonder_recommendation.input['historical_significance'] = historical_significance_score
    wonder_recommendation.input['architectural_beauty'] = architectural_beauty_score
    wonder_recommendation.compute()
    
    recommended_wonder = wonder_names[int(wonder_recommendation.output['wonder_choice'])]
    #print("Recommended Wonder of the World:", recommended_wonder)
    return recommended_wonder