# TODO: check once
def conflict_exclusion(self, sentence, h):
    action_table = self.action_table
    variables = self.variables

    # separate actions by time step
    temp_actions = [[] for i in range(0, h + 1)]
    for action in action_table:
        t = variables[action][1]
        temp_actions[t].append(action)

    # check if actions in the same time step are inconsistent
    for i in range(0, len(temp_actions[0])):
        action1 = action_table[temp_actions[0][i]]  # get action 1 for comparison

        for j in range(i + 1, len(temp_actions[0])):
            action2 = action_table[temp_actions[0][j]]  # get action 2 for comparison

            added = False  # control variable to check if conflict was already found
            for precond in action1[0]:
                for effect in action2[1]:

                    if precond > 0:  # non negated precondition so effect should be negated
                        if (precond + 1) is -effect:

                            for t in range(0, h + 1):
                                clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                sentence.append(clause)
                            added = True
                            break
                    else:  # precondition negated, so non negated effect
                        if (precond - 1) is -effect:

                            for t in range(0, h + 1):
                                clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                sentence.append(clause)
                            added = True
                            break

                if added:  # conflict already found, move to next action
                    break

            if not added:  # only check this loops if conflict was not already found
                for precond in action2[0]:
                    for effect in action1[1]:

                        if precond > 0:  # non negated precondition so effect should be negated
                            if (precond + 1) is -effect:

                                for t in range(0, h + 1):
                                    clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                    sentence.append(clause)
                                added = True
                                break
                        else:  # precondition negated, so non negated effect
                            if (precond - 1) is -effect:

                                for t in range(0, h + 1):
                                    clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                    sentence.append(clause)
                                added = True
                                break
                    if added:  # conflict already found, move to next action
                        break

    return sentence


# TODO: check all
def conflict_exclusion(self, sentence, h):
    action_table = self.action_table
    variables = self.variables
    for t in range(0, h + 1):

        temp_actions = []
        for action in action_table:
            if variables[action][1] == t:
                temp_actions.append(action)

        # check if actions in the same time step are inconsistent
        for i in range(0, len(temp_actions)):
            action1 = action_table[temp_actions[i]]  # get action 1 for comparison

            for j in range(i + 1, len(temp_actions)):
                action2 = action_table[temp_actions[j]]  # get action 2 for comparison

                added = False  # control variable to check if conflict was already found
                for precond in action1[0]:
                    for effect in action2[1]:

                        if precond > 0:  # non negated precondition so effect should be negated
                            if (precond + 1) is -effect:
                                clause = [-temp_actions[i], -temp_actions[j]]
                                sentence.append(clause)
                                added = True
                                break
                        else:  # precondition negated, so non negated effect
                            if (precond - 1) is -effect:
                                clause = [-temp_actions[i], -temp_actions[j]]
                                sentence.append(clause)
                                added = True
                                break

                    if added:  # conflict already found, move to next action
                        break

                if not added:  # only check this loops if conflict was not already found
                    for precond in action2[0]:
                        for effect in action1[1]:

                            if precond > 0:  # non negated precondition so effect should be negated
                                if (precond + 1) is -effect:
                                    clause = [-temp_actions[i], -temp_actions[j]]
                                    sentence.append(clause)
                                    added = True
                                    break
                            else:  # precondition negated, so non negated effect
                                if (precond - 1) is -effect:
                                    clause = [-temp_actions[i], -temp_actions[j]]
                                    sentence.append(clause)
                                    added = True
                                    break
                        if added:  # conflict already found, move to next action
                            break

    return sentence
