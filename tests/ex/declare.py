@meta.declare
class X: pass

# 실제 정의가 뒤따른다.
class X(meta.Entity):
    x = X() # 자기 참조

# 전방 선언.
@meta.declare
class Child: pass

class Mother(meta.Entity):
    children = Child[:]() # 순환 참조. 튜플화도 가능.

# 실제 정의가 뒤따른다.
class Child(meta.Entity):
    mother = Mother()
