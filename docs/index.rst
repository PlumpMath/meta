.. Meta documentation master file

Meta: A platform-agnostic library for schema modeling
=====================================================

Version |version|.

Meta 는 파이썬의 자료 구조를 정의하고, 직렬화하며, 검사하는데 사용할 수 있는 플랫폼 독립적인 라이브러리 입니다.

   .. literalinclude:: /../tests/ex/welcome.rst

애초에 RESTful API 서버와 클라이언트를 지원하고, NoSQL ODM 에 기초를 제공하기 위해 설계되었으나, 두 응용에만 한정되지는 않습니다.

Install
=======

::

    pip install flowdas-meta

파이썬 2.7 과 3.3+ 를 지원합니다. PyPy 역시 지원됩니다. 같이 설치되는 패키지는 없습니다.

아직 PyPI 에 배포되지 않은 개발 버전을 설치하는 방법은 이렇습니다.::

    pip install git+https://github.com/flowdas/meta.git@develop#egg=flowdas-meta

Why?
====

라이브러리의 목적과 거시적인 형태를 볼 때 유사한 라이브러리들은 많습니다. 하지만 자세히 들여다보면 설계상의 의사결정들에 미묘한 차이들이 발견됩니다.
라이브러리를 새로 만든 이유는 적절한 수준에서 수용할 수 있는 조합을 발견하지 못했기 때문입니다. 여러분들도 같은 시각으로 Meta 를 바라보게될줄로 압니다.
Meta 가 갖고 있는 특징이자 한계입니다.

플랫폼 독립적
    데이터베이스나 기타 어떤 플랫폼에도 종속적이지 않습니다.
정의와 구현의 일체화
    자료 구조의 정의와 자료 구조의 구현을 일체화합니다.
    상기한 예에서 ``Author`` 는 ``Book`` 을 정의하는데 사용되지만, 예에서 확인할 수 있듯이 스스로 값 자체이기도 합니다.
    이 때문에 객체들간의 관계를 정의하기 위해 별도의 클래스를 사용하지 않고 직접 기술됩니다. 순환 구조를 정의하기 위한 방법도 제공합니다.
다형성(Polymorphism)
    두가지 종류의 다형성을 지원합니다.

    클래스 다형성
        클래스 계층 구조를 만들고, 계층 구조를 고려한 검사를 수행하며, 역시 계층 구조가 반영된 가역적인 직렬화를 제공합니다.
    Union & Selector
        여러 종류의 형을 조합하여 그 중의 하나를 표시할 수 있는 방법을 제공합니다.
일반화된 배열
    배열 지원을 강화합니다. 위의 예에서 나오는 ``Author[1:]()`` 표현은 길이 1 이상인 ``Author`` 의 배열을 뜻합니다.
    균일(homogeneous)/비균일(heterogeneous), 고정/가변 길이 배열이 무한 중첩될 수 있습니다.
암묵적인 검사
    검사를 암묵적인 검사(Implicit Validation)와 명시적인 검사(Explicit Validation)로 구분합니다.
    위의 예에서 나오는 ``book.published = '2016-03-15'`` 라는 문장은 암묵적인 검사를 수행하고,
    ``book.validate()`` 라는 문장은 명시적인 검사를 수행합니다.
    암묵적인 검사는 값들이 올바른 형태를 갖고 있는지를 검사하고, 명시적인 검사는 필요한 값들의 존재 여부와 값들간의 관계를 검사합니다.

Guide
=====

.. toctree::
   :maxdepth: 2

   quickstart
   tuple
   nesting
   union
   inheritance
   serialization

API Reference
=============

.. toctree::
   :maxdepth: 3

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

