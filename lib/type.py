#encoding: utf8
# 确保是字符串类型
def astr(text):
	return text if isinstance(text, str) else text.__str__()

# 是否是列表或元组
def is_list_or_tuple(var):
	return isinstance(var, list) or isinstance(var, tuple)

class Map(dict):
	__slots__ = ()

	def __getattr__(self, name):
		return self[name] if name in self else None

	def __setattr__(self, name, value):
		self[name] = value

# data = DictRef({'a': 1})
# print(data.a) # get 1
class DictRef(object):
	__slots__ = ('_data',)

	def __init__(self, obj):
		object.__setattr__(self, '_data', obj)

	def __getattr__(self, name):
		return self._data.get(name, None)

	def __setattr__(self, name, value):
		self._data[name] = value

	def __str__(self):
		return self._data.__str__()

	def __iter__(self):
		return self._data.__iter__()

	def __attrs__(self, select = None):
		result = []
		_attr = lambda attr: attr + '"' + astr(self._data[attr]) + '"='
		if select is None:
			for attr in self:
				result.append(_attr(attr))
		else:
			for attr in select:
				if attr in self:
					result.append(_attr(attr))
		return ' '.join(result)

	def __get__(self, name, default):
		return self.__getattr__(name) or default

# 接收字典列表
# datas = DictRef([{'a': 1}, {'a': 2}])
# for data in datas:
#     print(data.a)
class DictsRef(object):
	__slots__ = ('__ref', '__iter')

	def __init__(self, array):
		if is_list_or_tuple(array):
			self.__ref = None
			self.__iter = array.__iter__()
		else:
			raise TypeError('array must be a list or tuple')

	def __iter__(self):
		return self

	def next(self):
		return self.__next__()

	def __next__(self):
		data = next(self.__iter)
		if not self.__ref:
			self.__ref = DictRef(data)
		else:
			self.__ref.__init__(data)
		return self.__ref