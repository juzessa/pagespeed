import psycopg2
import requests

from src.config import (POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_PORT,
                        POSTGRES_USER)


def get_db_connect():
    connect = psycopg2.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        host='localhost'
    )
    return connect


def get_urls():
    try:
        connect = get_db_connect()
        cur = connect.cursor()
        cur.execute("""
        select id, name from urls""")
        urls = cur.fetchall()
        return urls
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def get_one_url(url_id):
    try:
        connect = get_db_connect()
        cur = connect.cursor()
        query = """
        select name, created_at
        from urls
        where id=%s;"""
        data = (url_id,)
        cur.execute(query, data)
        result = cur.fetchone()
        if result is not None:
            return result
        return None, None
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def get_one_url_by_name(name):
    try:
        connect = get_db_connect()
        cur = connect.cursor()
        query = """
        select id, created_at
        from urls
        where name=%s;"""
        data = (name,)
        cur.execute(query, data)
        result = cur.fetchone()
        if result is not None:
            return result
        return None
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def post_url(name):
    try:
        connect = get_db_connect()
        cur = connect.cursor()
        site = get_one_url_by_name(name)
        if site is not None:
            return {'site': site, 'message': 'Cайт уже добавлен'}
        query = """
        insert into urls (name)
        values (%s);"""
        data = (name,)
        cur.execute(query, data)
        connect.commit()
        site = get_one_url_by_name(name)
        return {'site': site, 'message': 'Сайт успешно добавлен'}
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def get_checks(url_id):
    try:
        connect = get_db_connect()
        cur = connect.cursor()
        query = ("""
        select * from url_checks
        where url_id = %s
        """)
        data = (url_id,)
        cur.execute(query, data)
        urls = cur.fetchall()
        if urls:
            return urls
        return []
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def post_check(url_id, status_code, h1, title, description):
    try:
        connect = get_db_connect()
        cur = connect.cursor()
        query = """
        insert into url_checks (url_id, status_code, h1, title, description)
        values (%s, %s, %s, %s, %s);"""
        data = (url_id, status_code, h1, title, description)
        cur.execute(query, data)
        connect.commit()
        checks = get_checks(url_id)
        return {'checks': checks}
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def get_last_checked_code(url_id):
    try:
        connect = get_db_connect()
        cur = connect.cursor()
        query = ("""
        select created_at, status_code from url_checks
        where url_id = %s
        order by created_at desc
        """)
        data = (url_id,)
        cur.execute(query, data)
        result = cur.fetchone()
        if result:
            last_checked, status_code = result
            return last_checked, status_code
        return None, None
    except Exception as e:
        raise RuntimeError(f"Error: {e}")
