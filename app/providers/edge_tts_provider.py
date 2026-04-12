import asyncio
import edge_tts
from typing import Tuple, Optional, Dict, List

# Comprehensive set of English Edge TTS voices with metadata
PUBLIC_VOICES = {
    # Hong Kong
    "en_hk_yan": {
        "voice_id": "en-HK-YanNeural",
        "name": "Yan",
        "country": "Hong Kong",
        "language": "English",
        "gender": "Female"
    },
    "en_hk_sam": {
        "voice_id": "en-HK-SamNeural",
        "name": "Sam",
        "country": "Hong Kong",
        "language": "English",
        "gender": "Male"
    },
    
    # Ireland
    "en_ie_connor": {
        "voice_id": "en-IE-ConnorNeural",
        "name": "Connor",
        "country": "Ireland",
        "language": "English",
        "gender": "Male"
    },
    "en_ie_emily": {
        "voice_id": "en-IE-EmilyNeural",
        "name": "Emily",
        "country": "Ireland",
        "language": "English",
        "gender": "Female"
    },
    
    # India
    "en_in_neerja_expressive": {
        "voice_id": "en-IN-NeerjaExpressiveNeural",
        "name": "Neerja (Expressive)",
        "country": "India",
        "language": "English",
        "gender": "Female"
    },
    "en_in_neerja": {
        "voice_id": "en-IN-NeerjaNeural",
        "name": "Neerja",
        "country": "India",
        "language": "English",
        "gender": "Female"
    },
    "en_in_prabhat": {
        "voice_id": "en-IN-PrabhatNeural",
        "name": "Prabhat",
        "country": "India",
        "language": "English",
        "gender": "Male"
    },
    
    # Kenya
    "en_ke_asilia": {
        "voice_id": "en-KE-AsiliaNeural",
        "name": "Asilia",
        "country": "Kenya",
        "language": "English",
        "gender": "Female"
    },
    "en_ke_chilemba": {
        "voice_id": "en-KE-ChilembaNeural",
        "name": "Chilemba",
        "country": "Kenya",
        "language": "English",
        "gender": "Male"
    },
    
    # Nigeria
    "en_ng_abeo": {
        "voice_id": "en-NG-AbeoNeural",
        "name": "Abeo",
        "country": "Nigeria",
        "language": "English",
        "gender": "Male"
    },
    "en_ng_ezinne": {
        "voice_id": "en-NG-EzinneNeural",
        "name": "Ezinne",
        "country": "Nigeria",
        "language": "English",
        "gender": "Female"
    },
    
    # Australia
    "en_au_natasha": {
        "voice_id": "en-AU-NatashaNeural",
        "name": "Natasha",
        "country": "Australia",
        "language": "English",
        "gender": "Female"
    },
    "en_au_william": {
        "voice_id": "en-AU-WilliamNeural",
        "name": "William",
        "country": "Australia",
        "language": "English",
        "gender": "Male"
    },
    
    # Canada
    "en_ca_clara": {
        "voice_id": "en-CA-ClaraNeural",
        "name": "Clara",
        "country": "Canada",
        "language": "English",
        "gender": "Female"
    },
    "en_ca_liam": {
        "voice_id": "en-CA-LiamNeural",
        "name": "Liam",
        "country": "Canada",
        "language": "English",
        "gender": "Male"
    },
    
    # United Kingdom
    "en_gb_libby": {
        "voice_id": "en-GB-LibbyNeural",
        "name": "Libby",
        "country": "United Kingdom",
        "language": "English",
        "gender": "Female"
    },
    "en_gb_maisie": {
        "voice_id": "en-GB-MaisieNeural",
        "name": "Maisie",
        "country": "United Kingdom",
        "language": "English",
        "gender": "Female"
    },
    "en_gb_ryan": {
        "voice_id": "en-GB-RyanNeural",
        "name": "Ryan",
        "country": "United Kingdom",
        "language": "English",
        "gender": "Male"
    },
    "en_gb_sonia": {
        "voice_id": "en-GB-SoniaNeural",
        "name": "Sonia",
        "country": "United Kingdom",
        "language": "English",
        "gender": "Female"
    },
    "en_gb_thomas": {
        "voice_id": "en-GB-ThomasNeural",
        "name": "Thomas",
        "country": "United Kingdom",
        "language": "English",
        "gender": "Male"
    },
    
    # New Zealand
    "en_nz_mitchell": {
        "voice_id": "en-NZ-MitchellNeural",
        "name": "Mitchell",
        "country": "New Zealand",
        "language": "English",
        "gender": "Male"
    },
    "en_nz_molly": {
        "voice_id": "en-NZ-MollyNeural",
        "name": "Molly",
        "country": "New Zealand",
        "language": "English",
        "gender": "Female"
    },
    
    # Philippines
    "en_ph_james": {
        "voice_id": "en-PH-JamesNeural",
        "name": "James",
        "country": "Philippines",
        "language": "English",
        "gender": "Male"
    },
    "en_ph_rosa": {
        "voice_id": "en-PH-RosaNeural",
        "name": "Rosa",
        "country": "Philippines",
        "language": "English",
        "gender": "Female"
    },
    
    # Singapore
    "en_sg_luna": {
        "voice_id": "en-SG-LunaNeural",
        "name": "Luna",
        "country": "Singapore",
        "language": "English",
        "gender": "Female"
    },
    "en_sg_wayne": {
        "voice_id": "en-SG-WayneNeural",
        "name": "Wayne",
        "country": "Singapore",
        "language": "English",
        "gender": "Male"
    },
    
    # Tanzania
    "en_tz_elimu": {
        "voice_id": "en-TZ-ElimuNeural",
        "name": "Elimu",
        "country": "Tanzania",
        "language": "English",
        "gender": "Male"
    },
    "en_tz_imani": {
        "voice_id": "en-TZ-ImaniNeural",
        "name": "Imani",
        "country": "Tanzania",
        "language": "English",
        "gender": "Female"
    },
    
    # United States
    "en_us_ana": {
        "voice_id": "en-US-AnaNeural",
        "name": "Ana",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_andrew_multilingual": {
        "voice_id": "en-US-AndrewMultilingualNeural",
        "name": "Andrew (Multilingual)",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_andrew": {
        "voice_id": "en-US-AndrewNeural",
        "name": "Andrew",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_aria": {
        "voice_id": "en-US-AriaNeural",
        "name": "Aria",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_ava_multilingual": {
        "voice_id": "en-US-AvaMultilingualNeural",
        "name": "Ava (Multilingual)",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_ava": {
        "voice_id": "en-US-AvaNeural",
        "name": "Ava",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_brian_multilingual": {
        "voice_id": "en-US-BrianMultilingualNeural",
        "name": "Brian (Multilingual)",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_brian": {
        "voice_id": "en-US-BrianNeural",
        "name": "Brian",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_christopher": {
        "voice_id": "en-US-ChristopherNeural",
        "name": "Christopher",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_emma_multilingual": {
        "voice_id": "en-US-EmmaMultilingualNeural",
        "name": "Emma (Multilingual)",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_emma": {
        "voice_id": "en-US-EmmaNeural",
        "name": "Emma",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_eric": {
        "voice_id": "en-US-EricNeural",
        "name": "Eric",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_guy": {
        "voice_id": "en-US-GuyNeural",
        "name": "Guy",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_jenny": {
        "voice_id": "en-US-JennyNeural",
        "name": "Jenny",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_michelle": {
        "voice_id": "en-US-MichelleNeural",
        "name": "Michelle",
        "country": "United States",
        "language": "English",
        "gender": "Female"
    },
    "en_us_roger": {
        "voice_id": "en-US-RogerNeural",
        "name": "Roger",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    "en_us_steffan": {
        "voice_id": "en-US-SteffanNeural",
        "name": "Steffan",
        "country": "United States",
        "language": "English",
        "gender": "Male"
    },
    
    # South Africa
    "en_za_leah": {
        "voice_id": "en-ZA-LeahNeural",
        "name": "Leah",
        "country": "South Africa",
        "language": "English",
        "gender": "Female"
    },
    "en_za_luke": {
        "voice_id": "en-ZA-LukeNeural",
        "name": "Luke",
        "country": "South Africa",
        "language": "English",
        "gender": "Male"
    },
    
    # Arabic Voices
    # United Arab Emirates
    "ar_ae_fatima": {
        "voice_id": "ar-AE-FatimaNeural",
        "name": "Fatima",
        "country": "United Arab Emirates",
        "language": "Arabic",
        "gender": "Female"
    },
    "ar_ae_hamdan": {
        "voice_id": "ar-AE-HamdanNeural",
        "name": "Hamdan",
        "country": "United Arab Emirates",
        "language": "Arabic",
        "gender": "Male"
    },
    
    # Bahrain
    "ar_bh_ali": {
        "voice_id": "ar-BH-AliNeural",
        "name": "Ali",
        "country": "Bahrain",
        "language": "Arabic",
        "gender": "Male"
    },
    "ar_bh_laila": {
        "voice_id": "ar-BH-LailaNeural",
        "name": "Laila",
        "country": "Bahrain",
        "language": "Arabic",
        "gender": "Female"
    },
    
    # Algeria
    "ar_dz_amina": {
        "voice_id": "ar-DZ-AminaNeural",
        "name": "Amina",
        "country": "Algeria",
        "language": "Arabic",
        "gender": "Female"
    },
    "ar_dz_ismael": {
        "voice_id": "ar-DZ-IsmaelNeural",
        "name": "Ismael",
        "country": "Algeria",
        "language": "Arabic",
        "gender": "Male"
    },
    
    # Egypt
    "ar_eg_salma": {
        "voice_id": "ar-EG-SalmaNeural",
        "name": "Salma",
        "country": "Egypt",
        "language": "Arabic",
        "gender": "Female"
    },
    "ar_eg_shakir": {
        "voice_id": "ar-EG-ShakirNeural",
        "name": "Shakir",
        "country": "Egypt",
        "language": "Arabic",
        "gender": "Male"
    },
    
    # Iraq
    "ar_iq_bassel": {
        "voice_id": "ar-IQ-BasselNeural",
        "name": "Bassel",
        "country": "Iraq",
        "language": "Arabic",
        "gender": "Male"
    },
    "ar_iq_rana": {
        "voice_id": "ar-IQ-RanaNeural",
        "name": "Rana",
        "country": "Iraq",
        "language": "Arabic",
        "gender": "Female"
    },
    
    # India - Hindi
    "hi_in_madhur": {
        "voice_id": "hi-IN-MadhurNeural",
        "name": "Madhur",
        "country": "India",
        "language": "Hindi",
        "gender": "Male"
    },
    "hi_in_swara": {
        "voice_id": "hi-IN-SwaraNeural",
        "name": "Swara",
        "country": "India",
        "language": "Hindi",
        "gender": "Female"
    },
    
    # Pakistan - Urdu
    "ur_in_gul": {
        "voice_id": "ur-IN-GulNeural",
        "name": "Gul",
        "country": "Pakistan",
        "language": "Urdu",
        "gender": "Female"
    },
    "ur_in_salman": {
        "voice_id": "ur-IN-SalmanNeural",
        "name": "Salman",
        "country": "Pakistan",
        "language": "Urdu",
        "gender": "Male"
    },
    "ur_pk_asad": {
        "voice_id": "ur-PK-AsadNeural",
        "name": "Asad",
        "country": "Pakistan",
        "language": "Urdu",
        "gender": "Male"
    },
    "ur_pk_uzma": {
        "voice_id": "ur-PK-UzmaNeural",
        "name": "Uzma",
        "country": "Pakistan",
        "language": "Urdu",
        "gender": "Female"
    },
    
    # Belgium - French
    "fr_be_charline": {
        "voice_id": "fr-BE-CharlineNeural",
        "name": "Charline",
        "country": "Belgium",
        "language": "French",
        "gender": "Female"
    },
    "fr_be_gerard": {
        "voice_id": "fr-BE-GerardNeural",
        "name": "Gerard",
        "country": "Belgium",
        "language": "French",
        "gender": "Male"
    },
    
    # Canada - French
    "fr_ca_antoine": {
        "voice_id": "fr-CA-AntoineNeural",
        "name": "Antoine",
        "country": "Canada",
        "language": "French",
        "gender": "Male"
    },
    "fr_ca_jean": {
        "voice_id": "fr-CA-JeanNeural",
        "name": "Jean",
        "country": "Canada",
        "language": "French",
        "gender": "Male"
    },
    "fr_ca_sylvie": {
        "voice_id": "fr-CA-SylvieNeural",
        "name": "Sylvie",
        "country": "Canada",
        "language": "French",
        "gender": "Female"
    },
    "fr_ca_thierry": {
        "voice_id": "fr-CA-ThierryNeural",
        "name": "Thierry",
        "country": "Canada",
        "language": "French",
        "gender": "Male"
    },
    
    # Switzerland - French
    "fr_ch_ariane": {
        "voice_id": "fr-CH-ArianeNeural",
        "name": "Ariane",
        "country": "Switzerland",
        "language": "French",
        "gender": "Female"
    },
    "fr_ch_fabrice": {
        "voice_id": "fr-CH-FabriceNeural",
        "name": "Fabrice",
        "country": "Switzerland",
        "language": "French",
        "gender": "Male"
    },
    
    # France - French
    "fr_fr_denise": {
        "voice_id": "fr-FR-DeniseNeural",
        "name": "Denise",
        "country": "France",
        "language": "French",
        "gender": "Female"
    },
    "fr_fr_eloise": {
        "voice_id": "fr-FR-EloiseNeural",
        "name": "Eloise",
        "country": "France",
        "language": "French",
        "gender": "Female"
    },
    
    # China - Chinese
    "zh_cn_liaoning_xiaobei": {
        "voice_id": "zh-CN-liaoning-XiaobeiNeural",
        "name": "Xiaobei (Liaoning)",
        "country": "China",
        "language": "Chinese",
        "gender": "Female"
    },
    "zh_cn_shaanxi_xiaoni": {
        "voice_id": "zh-CN-shaanxi-XiaoniNeural",
        "name": "Xiaoni (Shaanxi)",
        "country": "China",
        "language": "Chinese",
        "gender": "Female"
    },
    "zh_cn_xiaoxiao": {
        "voice_id": "zh-CN-XiaoxiaoNeural",
        "name": "Xiaoxiao",
        "country": "China",
        "language": "Chinese",
        "gender": "Female"
    },
    "zh_cn_xiaoyi": {
        "voice_id": "zh-CN-XiaoyiNeural",
        "name": "Xiaoyi",
        "country": "China",
        "language": "Chinese",
        "gender": "Female"
    },
    "zh_cn_yunjian": {
        "voice_id": "zh-CN-YunjianNeural",
        "name": "Yunjian",
        "country": "China",
        "language": "Chinese",
        "gender": "Male"
    },
    "zh_cn_yunxia": {
        "voice_id": "zh-CN-YunxiaNeural",
        "name": "Yunxia",
        "country": "China",
        "language": "Chinese",
        "gender": "Male"
    },
    "zh_cn_yunxi": {
        "voice_id": "zh-CN-YunxiNeural",
        "name": "Yunxi",
        "country": "China",
        "language": "Chinese",
        "gender": "Male"
    },
    "zh_cn_yunyang": {
        "voice_id": "zh-CN-YunyangNeural",
        "name": "Yunyang",
        "country": "China",
        "language": "Chinese",
        "gender": "Male"
    },
    
    # Hong Kong - Chinese
    "zh_hk_hiugaai": {
        "voice_id": "zh-HK-HiuGaaiNeural",
        "name": "HiuGaai",
        "country": "Hong Kong",
        "language": "Chinese",
        "gender": "Female"
    },
    "zh_hk_hiumaan": {
        "voice_id": "zh-HK-HiuMaanNeural",
        "name": "HiuMaan",
        "country": "Hong Kong",
        "language": "Chinese",
        "gender": "Female"
    },
    
    # Austria - German
    "de_at_ingrid": {
        "voice_id": "de-AT-IngridNeural",
        "name": "Ingrid",
        "country": "Austria",
        "language": "German",
        "gender": "Female"
    },
    "de_at_jonas": {
        "voice_id": "de-AT-JonasNeural",
        "name": "Jonas",
        "country": "Austria",
        "language": "German",
        "gender": "Male"
    },
    
    # Switzerland - German
    "de_ch_jan": {
        "voice_id": "de-CH-JanNeural",
        "name": "Jan",
        "country": "Switzerland",
        "language": "German",
        "gender": "Male"
    },
    "de_ch_leni": {
        "voice_id": "de-CH-LeniNeural",
        "name": "Leni",
        "country": "Switzerland",
        "language": "German",
        "gender": "Female"
    },
    
    # Germany - German
    "de_de_amala": {
        "voice_id": "de-DE-AmalaNeural",
        "name": "Amala",
        "country": "Germany",
        "language": "German",
        "gender": "Female"
    },
    "de_de_conrad": {
        "voice_id": "de-DE-ConradNeural",
        "name": "Conrad",
        "country": "Germany",
        "language": "German",
        "gender": "Male"
    },
    "de_de_florian_multilingual": {
        "voice_id": "de-DE-FlorianMultilingualNeural",
        "name": "Florian (Multilingual)",
        "country": "Germany",
        "language": "German",
        "gender": "Male"
    },
    "de_de_katja": {
        "voice_id": "de-DE-KatjaNeural",
        "name": "Katja",
        "country": "Germany",
        "language": "German",
        "gender": "Female"
    },
    "de_de_killian": {
        "voice_id": "de-DE-KillianNeural",
        "name": "Killian",
        "country": "Germany",
        "language": "German",
        "gender": "Male"
    },
    "de_de_seraphina_multilingual": {
        "voice_id": "de-DE-SeraphinaMultilingualNeural",
        "name": "Seraphina (Multilingual)",
        "country": "Germany",
        "language": "German",
        "gender": "Female"
    },
    
    # Japan - Japanese
    "ja_jp_keita": {
        "voice_id": "ja-JP-KeitaNeural",
        "name": "Keita",
        "country": "Japan",
        "language": "Japanese",
        "gender": "Male"
    },
    "ja_jp_nanami": {
        "voice_id": "ja-JP-NanamiNeural",
        "name": "Nanami",
        "country": "Japan",
        "language": "Japanese",
        "gender": "Female"
    },
    
    # Vietnam - Vietnamese
    "vi_vn_hoaimy": {
        "voice_id": "vi-VN-HoaiMyNeural",
        "name": "HoaiMy",
        "country": "Vietnam",
        "language": "Vietnamese",
        "gender": "Female"
    },
    "vi_vn_namminh": {
        "voice_id": "vi-VN-NamMinhNeural",
        "name": "NamMinh",
        "country": "Vietnam",
        "language": "Vietnamese",
        "gender": "Male"
    },
    
    # Turkey - Turkish
    "tr_tr_ahmet": {
        "voice_id": "tr-TR-AhmetNeural",
        "name": "Ahmet",
        "country": "Turkey",
        "language": "Turkish",
        "gender": "Male"
    },
    "tr_tr_emel": {
        "voice_id": "tr-TR-EmelNeural",
        "name": "Emel",
        "country": "Turkey",
        "language": "Turkish",
        "gender": "Female"
    },
    
    # South Korea - Korean
    "ko_kr_hyunsu": {
        "voice_id": "ko-KR-HyunsuNeural",
        "name": "Hyunsu",
        "country": "South Korea",
        "language": "Korean",
        "gender": "Male"
    },
    "ko_kr_injoon": {
        "voice_id": "ko-KR-InJoonNeural",
        "name": "InJoon",
        "country": "South Korea",
        "language": "Korean",
        "gender": "Male"
    },
    "ko_kr_sunhi": {
        "voice_id": "ko-KR-SunHiNeural",
        "name": "SunHi",
        "country": "South Korea",
        "language": "Korean",
        "gender": "Female"
    },
    
    # Argentina - Spanish
    "es_ar_elena": {
        "voice_id": "es-AR-ElenaNeural",
        "name": "Elena",
        "country": "Argentina",
        "language": "Spanish",
        "gender": "Female"
    },
    "es_ar_tomas": {
        "voice_id": "es-AR-TomasNeural",
        "name": "Tomas",
        "country": "Argentina",
        "language": "Spanish",
        "gender": "Male"
    },
    
    # Bolivia - Spanish
    "es_bo_marcelo": {
        "voice_id": "es-BO-MarceloNeural",
        "name": "Marcelo",
        "country": "Bolivia",
        "language": "Spanish",
        "gender": "Male"
    },
    "es_bo_sofia": {
        "voice_id": "es-BO-SofiaNeural",
        "name": "Sofia",
        "country": "Bolivia",
        "language": "Spanish",
        "gender": "Female"
    },
    
    # Chile - Spanish
    "es_cl_catalina": {
        "voice_id": "es-CL-CatalinaNeural",
        "name": "Catalina",
        "country": "Chile",
        "language": "Spanish",
        "gender": "Female"
    },
    "es_cl_lorenzo": {
        "voice_id": "es-CL-LorenzoNeural",
        "name": "Lorenzo",
        "country": "Chile",
        "language": "Spanish",
        "gender": "Male"
    },
    
    # Colombia - Spanish
    "es_co_gonzalo": {
        "voice_id": "es-CO-GonzaloNeural",
        "name": "Gonzalo",
        "country": "Colombia",
        "language": "Spanish",
        "gender": "Male"
    },
    "es_co_salome": {
        "voice_id": "es-CO-SalomeNeural",
        "name": "Salome",
        "country": "Colombia",
        "language": "Spanish",
        "gender": "Female"
    },
    
    # Costa Rica - Spanish
    "es_cr_juan": {
        "voice_id": "es-CR-JuanNeural",
        "name": "Juan",
        "country": "Costa Rica",
        "language": "Spanish",
        "gender": "Male"
    },
    "es_cr_maria": {
        "voice_id": "es-CR-MariaNeural",
        "name": "Maria",
        "country": "Costa Rica",
        "language": "Spanish",
        "gender": "Female"
    },
    
    # South Africa - Afrikaans
    "af_za_adri": {
        "voice_id": "af-ZA-AdriNeural",
        "name": "Adri",
        "country": "South Africa",
        "language": "Afrikaans",
        "gender": "Female"
    },
    "af_za_willem": {
        "voice_id": "af-ZA-WillemNeural",
        "name": "Willem",
        "country": "South Africa",
        "language": "Afrikaans",
        "gender": "Male"
    },
}

class EdgeTTSProvider:
    def __init__(self, default_voice_key: str = "en_us_jenny"):
        self.default_voice_key = default_voice_key

    @staticmethod
    def public_voices() -> Dict[str, Dict[str, str]]:
        return PUBLIC_VOICES

    async def estimate_cost(self, text: str, *, per_char: int = 1) -> int:
        return max(1, per_char * len(text))

    async def synthesize(
        self,
        text: str,
        public_voice_key: Optional[str] = None,
        voice_name: Optional[str] = None,
    ) -> Tuple[bytes, str]:
        """
        Generate speech audio for the given text.

        Priority for voice selection:
        1) voice_name (explicit full Edge voice id like 'en-US-JennyNeural')
        2) public_voice_key (key into PUBLIC_VOICES)
        3) default voice set on provider
        """
        if voice_name:
            voice = voice_name
        elif public_voice_key and public_voice_key in PUBLIC_VOICES:
            voice = PUBLIC_VOICES[public_voice_key]["voice_id"]
        else:
            voice = PUBLIC_VOICES[self.default_voice_key]["voice_id"]
            
        communicate = edge_tts.Communicate(text, voice=voice)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks), "mp3"
