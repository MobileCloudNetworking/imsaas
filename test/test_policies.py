__author__ = 'mpa'


from model.Entities import Policy, Alarm, Action
import uuid

if __name__ == '__main__':

    al_args1 = {}
    al_args1['id'] = uuid.uuid4()
    al_args1['meter_name'] = "cpu_util"
    al_args1['statistic'] = "avg"
    al_args1['period'] = "60"
    al_args1['evaluation_periods'] = "1"
    al_args1['threshold'] = "50"
    al_args1['repeat_actions'] = "true"
    al_args1['comparison_operator'] = "gt"
    alarm1 = Alarm(**al_args1)

    al_args2 = {}
    al_args2['id'] = uuid.uuid4()
    al_args2['meter_name'] = "cpu_util"
    al_args2['statistic'] = "avg"
    al_args2['period'] = "60"
    al_args2['evaluation_periods'] = "1"
    al_args2['threshold'] = "50"
    al_args2['repeat_actions'] = "true"
    al_args2['comparison_operator'] = "gt"
    alarm2 = Alarm(**al_args2)

    ac_args = {}
    ac_args['id'] = uuid.uuid4()
    ac_args['adjustment_type'] = "ChangeInCapacity"
    ac_args['cooldown'] = "60"
    ac_args['scaling_adjustment'] = "1"
    action = Action(**ac_args)

    po_args = {}
    po_args['id'] = uuid.uuid4()
    po_args['name'] = "scaleup"
    po_args['alarms'] = [alarm1,alarm2]
    po_args['actions'] = [action]

    policy = Policy(**po_args)

    print policy

