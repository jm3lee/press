from textwrap import dedent

from pie import flatfile


def test_loads_list_and_multiline_item() -> None:
    text = dedent(
        '''\
        pie.ingredients
        [
        flour
        """
        sugar
        cane
        """
        ]
        '''
    )
    assert flatfile.loads(text.splitlines()) == {
        'pie': {'ingredients': ['flour', 'sugar\ncane']}
    }


def test_roundtrip_with_lists() -> None:
    data = {
        'pie': {
            'description': 'A flaky crust\nwith butter',
            'ingredients': ['flour', 'water', 'butter\nunsalted'],
        }
    }
    dumped = flatfile.dumps(data)
    assert flatfile.loads(dumped.splitlines()) == data


def test_loads_nested_lists() -> None:
    text = dedent(
        '''\
        pie.layers
        [
        [
        crust
        filling
        ]
        [
        icing
        ]
        ]
        '''
    )
    assert flatfile.loads(text.splitlines()) == {
        'pie': {'layers': [['crust', 'filling'], ['icing']]}
    }


def test_loads_nested_dicts() -> None:
    text = dedent(
        '''\
        desserts.pie.filling.fruit
        apple
        desserts.pie.filling.sugar
        cane
        '''
    )
    assert flatfile.loads(text.splitlines()) == {
        'desserts': {'pie': {'filling': {'fruit': 'apple', 'sugar': 'cane'}}}
    }


def test_loads_dict_braces() -> None:
    text = dedent(
        '''\
        pie
        {
        flavor
        apple
        }
        '''
    )
    assert flatfile.loads(text.splitlines()) == {
        'pie': {'flavor': 'apple'}
    }


def test_roundtrip_nested_dicts_and_lists() -> None:
    data = {
        'desserts': {
            'pie': {
                'layers': [['crust', 'filling'], ['icing']],
                'topping': 'cream',
            }
        }
    }
    dumped = flatfile.dumps(data)
    assert flatfile.loads(dumped.splitlines()) == data


def test_roundtrip_list_of_dicts() -> None:
    data = {'pies': [{'flavor': 'apple'}, {'flavor': 'cherry'}]}
    dumped = flatfile.dumps(data)
    assert flatfile.loads(dumped.splitlines()) == data


def test_load_reads_file(tmp_path) -> None:
    path = tmp_path / 'data.flatfile'
    path.write_text('foo.bar\n42\n')
    assert flatfile.load(path) == {'foo': {'bar': '42'}}


def test_load_key(tmp_path) -> None:
    path = tmp_path / 'data.flatfile'
    path.write_text('foo.bar\nbaz\n')
    assert flatfile.load_key(path, 'foo.bar') == 'baz'

def test_load_key_cast(tmp_path) -> None:
    path = tmp_path / 'data.flatfile'
    path.write_text('foo.bar\n7\n')
    assert int(flatfile.load_key(path, 'foo.bar')) == 7
