import unittest

from src.extraction import lire_build, lire_journal, lire_scan, masquer_donnees

LIGNE = "2026-11-27 17:02:11 paiement ERROR timeout passerelle apres 30s card=4970123412341234"


class TestExtraction(unittest.TestCase):
    def test_masquer_donnees(self):
        self.assertEqual(masquer_donnees("client=bob pwd=abc123"),
                         "client=bob pwd=[MASQUE]")

    def test_lire_journal(self):
        sig = lire_journal(LIGNE, 42)
        self.assertEqual(sig.ref, "SH-0042")
        self.assertEqual(sig.date, "2026-11-27T17:02:11Z")
        self.assertEqual(sig.gravite, "MAJEUR")
        self.assertNotIn("4970123412341234", sig.texte)

    def test_journal_invalide(self):
        with self.assertRaises(ValueError):
            lire_journal("trop court", 1)

    def test_lire_scan(self):
        sig = lire_scan({"id_faille": "CVE-1", "paquet": "lib-panier",
                         "risque": "CRITIQUE", "date": "2026-11-27T17:09:00Z"}, 8)
        self.assertEqual(sig.gravite, "BLOQUANT")
        self.assertEqual(sig.texte, "Faille CVE-1 dans lib-panier")

    def test_lire_build(self):
        sig = lire_build({"etape": "deploiement", "resultat": "ECHEC",
                          "date": "2026-11-27T17:08:00Z"}, 7)
        self.assertEqual(sig.categorie, "BUILD_ECHEC")
        self.assertEqual(sig.gravite, "MAJEUR")


if __name__ == "__main__":
    unittest.main()