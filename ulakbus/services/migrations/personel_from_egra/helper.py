def merge_attr(model,data):
    for key in data:
        try:
            setattr(model, key, data[key])
        except Exception, e:
            pass
            # print e