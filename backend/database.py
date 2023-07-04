from backend.create_app import db



def add_instance(model, **kwargs):
    instance = model(**kwargs)
    db.session.add(instance)
    commit_changes()
    
    
def delete_instance(model, id):
    model.query.filter_by(id=id).delete()
    commit_changes()
    
    
def commit_changes():
    db.session.commit()