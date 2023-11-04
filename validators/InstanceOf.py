### some theory related with the topic InstanceOf ###


class Instance:
    def __repr__(self) -> str:
        return __class__.__name__
    
class Hereditary(Instance):
    def __repr__(self) -> str:
        return __class__.__name__

jose = Hereditary()

if isinstance(jose, Instance):
    print("yes")

else:
    print("no")