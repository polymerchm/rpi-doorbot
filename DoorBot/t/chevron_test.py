import chevron

def first(text, render):
    # return only first occurance of items
    result = render(text)
    return [ x.strip() for x in result.split(" || ") if x.strip() ][0]

def inject_x(text, render):
    # inject data into scope
    print(f"<<{text}>>")
    return render(text, {'x': 'fred'})

args = {
    'template': 'Hello, {{# first}} {{x}} || {{y}} || {{z}} {{/ first}}!  {{# inject_x}} {{x}} {{/ inject_x}}',

    'data': {
        'z': 'foo',
        'x': 'bar',
        'first': first,
        'inject_x': inject_x
    }
}

print(chevron.render(**args))
