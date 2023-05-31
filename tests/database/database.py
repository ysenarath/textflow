import unittest
from textflow.database import db


class CreateDatabaseTestCase(unittest.TestCase):
    def test_create_all_config_not_set(self):
        with self.assertRaises(AttributeError):
            # the engine is None
            db.create_all()

    def test_create_all_with_config(self):
        db.context.from_config({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        has_error = False
        try:
            # the engine is not None
            db.create_all()
        except Exception:
            has_error = True
        finally:
            self.assertEqual(has_error, False)

    def test_create_context_with_none_config(self):
        with self.assertRaises(TypeError):
            # try to get attribute from None -> TypeError
            db.context.from_config(None)

    def test_create_context_with_empty_config(self):
        with self.assertRaises(KeyError):
            # try to get attribute from {} -> KeyError
            db.context.from_config({})

    def test_create_context_with_invalid_uri(self):
        with self.assertRaises(AttributeError):
            db.context.from_config({
                'SQLALCHEMY_DATABASE_URI': None
            })

    def test_is_models_mapped(self):
        from textflow import models
        from textflow.models import __all__ as model_names
        model_count = 0
        for model_name in model_names:
            Model = getattr(models, model_name)
            if not hasattr(Model, '__tablename__'):
                # check if table name is defined
                continue
            model_count += 1
            self.assertIn(
                Model.__tablename__,
                db.mapper_registry.metadata.tables,
            )
        self.assertGreater(model_count, 0)
        self.assertGreaterEqual(
            len(db.mapper_registry.metadata.tables), model_count
        )


if __name__ == '__main__':
    unittest.main()
