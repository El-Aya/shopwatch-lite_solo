import unittest

from src.contrat import Diagnostic, Signal
from src.notification import (approuver, choisir_canal, composer, consigner,
                              diffuser)


def exemple(critique=True, niveau="BLOQUANT"):
    s = Signal("SH-0125", "2026-11-27T17:02:11Z", "PAIEMENT", "paiement",
               "production", "JOURNAL", "MAJEUR", "timeout passerelle apres 30s")
    d = Diagnostic("SH-0125", niveau, "Passerelle lente",
                   "Isoler le service paiement", critique, ["PAIEMENT"])
    return s, d


class TestNotification(unittest.TestCase):
    def test_canaux(self):
        self.assertEqual(choisir_canal("BLOQUANT"), "SLACK")
        self.assertEqual(choisir_canal("MINEUR"), "TABLEAU")

    def test_canal_invalide(self):
        with self.assertRaises(ValueError):
            choisir_canal("???")

    def test_approbation(self):
        _, d = exemple()
        self.assertTrue(approuver(d, " OUI "))
        self.assertFalse(approuver(d, "n"))

    def test_composer(self):
        s, d = exemple()
        self.assertEqual(len(composer(s, d).split("\n")), 5)

    def test_diffuser(self):
        s, d = exemple()
        registre = []
        msg = diffuser(s, d, registre)
        self.assertEqual(msg.canal, "SLACK")
        self.assertEqual(len(registre), 1)
        self.assertEqual(s.etat, "DIFFUSE")

    def test_consigner(self):
        _, d = exemple()
        carnet = []
        consigner(d, True, "astreinte-shop", carnet, "2026-11-27T17:10:00Z")
        self.assertEqual(carnet[0]["accord"], True)


if __name__ == "__main__":
    unittest.main()