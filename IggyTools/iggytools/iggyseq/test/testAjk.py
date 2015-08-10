'''
Created on Jul 2, 2015

@author: akitzmiller
'''
import unittest
import os, shutil
import subprocess


class Test(unittest.TestCase):

    def __init__(self,*args,**kwargs):
        super(Test,self).__init__(*args,**kwargs)
        self.runname = '150605_D00365_0511_BC6FHCANXX'
        self.md5s = {
'34_TCCGCGAA-CCTATCCT.R2.fastq.gz' : '57dd9dec39bfb9d589a12f95773f429b',
'62_TCCGGAGA-TAATCTTA.R1.fastq.gz' : 'bbe725bcfe00a3e1243a1a50599a53f2',
'65_ATTCAGAA-TAATCTTA.R2.fastq.gz' : '2f70b71db452a19cfa399e9792fdf1e9',
'25_ATTACTCG-CCTATCCT.R2.fastq.gz' : '6edaa4f41ffc65974e18d3981106a37d',
'3_CGCTCATT-TATAGCCT.R1.fastq.gz' : '322ef1f23b0ba3caf2f79a5e927e1478',
'22_TCCGCGAA-ATAGAGGC.R2.fastq.gz' : 'a8b06ae5aa0f3148033592da6a660aff',
'32_TAATGCGC-CCTATCCT.R1.fastq.gz' : '580423308a4f68cca9a5017984507be2',
'34_TCCGCGAA-CCTATCCT.R1.fastq.gz' : 'ab43150b0633d964936d64480991d9ca',
'lane1_Undetermined.R1.fastq.gz' : 'cfff384279916472681150f9e4b3f387',
'60_AGCGATAG-AGGCGAAG.R1.fastq.gz' : '6f00533b21c1a69d7f706d204cfe447f',
'44_TAATGCGC-GGCTCTGA.R2.fastq.gz' : 'd2a220c0a64fc90d1415ebfff98b8c1f',
'71_TCTCGCGC-TAATCTTA.R2.fastq.gz' : '86a3609a0ab03ac1b1afbaef797538cf',
'44_TAATGCGC-GGCTCTGA.R1.fastq.gz' : '75d0d2761687cba227c0a3b0f8e0ca22',
'20C_TAATGCGC-ATAGAGGC.R1.fastq.gz' : '072603de9d9b87cffe80c25e26d975f9',
'46_TCCGCGAA-GGCTCTGA.R1.fastq.gz' : '0c3c57c0aae519094e0350de33348864',
'71_TCTCGCGC-TAATCTTA.R1.fastq.gz' : '089b9a0a75c7972c72b465e9832e7959',
'39_CGCTCATT-GGCTCTGA.R1.fastq.gz' : '383cfa46058f956215244b012cb20677',
'7_CTGAAGCT-TATAGCCT.R1.fastq.gz' : '3961474ae476d88ba6362f36a5c715ea',
'77_ATTCAGAA-CAGGACGT.R2.fastq.gz' : '2ee37aef5d6d41b717391fd2621edeb2',
'5_ATTCAGAA-TATAGCCT.R2.fastq.gz' : 'bc38466f58e80363e4bd9eb629fbbd8f',
'13_ATTACTCG-ATAGAGGC.R2.fastq.gz' : 'b1f2afee99c8eac94b80a6494ae0703c',
'8_TAATGCGC-TATAGCCT.R1.fastq.gz' : 'a71c917a332e3ca94cd335a067326ae3',
'30_GAATTCGT-CCTATCCT.R1.fastq.gz' : '2407ecf4087304159c03067e4344eeb9',
'22_TCCGCGAA-ATAGAGGC.R1.fastq.gz' : '918ddb7207187fa7eac4d34a31703318',
'26_TCCGGAGA-CCTATCCT.R2.fastq.gz' : '88ee682b2cc7fa72d963d3a0d38c8699',
'70_TCCGCGAA-TAATCTTA.R1.fastq.gz' : '056c6a961377c65a0bd3c9a18f69c80a',
'60_AGCGATAG-AGGCGAAG.R2.fastq.gz' : '08e5bcba6590e7666d74debe319bc47f',
'49_ATTACTCG-AGGCGAAG.R1.fastq.gz' : 'a78db6742bbbcb242773bfc79c065c9e',
'56_TAATGCGC-AGGCGAAG.R1.fastq.gz' : '1a9ed72c346d045c8b0a7419b475972a',
'42_GAATTCGT-GGCTCTGA.R2.fastq.gz' : 'd36bddc6a57607f497aa71e40ef6eda7',
'16_GAGATTCC-ATAGAGGC.R1.fastq.gz' : 'e9f6b98a91d98083f044ffdfdf174b1a',
'72_AGCGATAG-TAATCTTA.R1.fastq.gz' : 'bec15d97ffc3e6d6a00cb50362e36872',
'58_TCCGCGAA-AGGCGAAG.R1.fastq.gz' : 'ba7c3fceb7d11c200f56e5b3c9230890',
'45_CGGCTATG-GGCTCTGA.R2.fastq.gz' : '2faca326e578084dc6ad9f74d993fe7a',
'30_GAATTCGT-CCTATCCT.R2.fastq.gz' : 'b78c4e702c717a29a353530fecd33fd5',
'20C_TAATGCGC-ATAGAGGC.R2.fastq.gz' : 'ff0ac293b462922d91ba2b03ffae656f',
'17_ATTCAGAA-ATAGAGGC.R2.fastq.gz' : '120d1519aed4a5be7c0c3224a81adfde',
'79__TAATGCGC-CAGGACGT.R2.fastq.gz' : '63b4683ee0bcc271c427cf1f047eaf94',
'43_CTGAAGCT-GGCTCTGA.R2.fastq.gz' : 'b56ef4d92aa220608ad783d5fde5bd5b',
'lane1_Undetermined.R2.fastq.gz' : '71dfe43172cf200c07b8bacd9df9bc40',
'54_GAATTCGT-AGGCGAAG.R1.fastq.gz' : '706ace38194ad58269e82849deb1546f',
'56_TAATGCGC-AGGCGAAG.R2.fastq.gz' : '783b394af30fc691c547b959b6b027f3',
'36_AGCGATAG-CCTATCCT.R2.fastq.gz' : 'b1caaa9a7171fc1151bf39578c4c80e5',
'80__CTGAAGCT-CAGGACGT.R2.fastq.gz' : '96599b05373827030be15f1fafca3d93',
'57_CGGCTATG-AGGCGAAG.R1.fastq.gz' : 'afc0bf4085c1c358fed80f571f0eb5d5',
'31_CTGAAGCT-CCTATCCT.R2.fastq.gz' : '6eeb02fcedb57e78a061cac0d1024633',
'35_TCTCGCGC-CCTATCCT.R1.fastq.gz' : 'f9343e0456215d746f34f8e9c4142340',
'50_TCCGGAGA-AGGCGAAG.R2.fastq.gz' : '6bc652f253eb4fcb5ed225bfa94d6891',
'1_ATTACTCG-TATAGCCT.R1.fastq.gz' : '4279d601ec30eb4d5e725c77f9244e0a',
'47_TCTCGCGC-GGCTCTGA.R1.fastq.gz' : '8d0424203ea19399ad821f3386ce643e',
'40_GAGATTCC-GGCTCTGA.R2.fastq.gz' : '7891a5e35d7c5d9eb9ef52835195c6e2',
'9_CGGCTATG-TATAGCCT.R2.fastq.gz' : 'cd9905f587b6b1dc36d91557542aa7ce',
'6_GAATTCGT-TATAGCCT.R1.fastq.gz' : '66eb9de263ad2d653956ec9b19727718',
'45_CGGCTATG-GGCTCTGA.R1.fastq.gz' : '100dfaab8a7e68cd9834fae8c22f32fe',
'8_TAATGCGC-TATAGCCT.R2.fastq.gz' : 'e5879790636f512af4ff4e74fc6c335f',
'75_CGCTCATT-CAGGACGT.R1.fastq.gz' : 'f00e76889faf0636f9bb1f1b2cd2d633',
'29_ATTCAGAA-CCTATCCT.R2.fastq.gz' : 'c3fdfe34938892b076f732a51c1daef4',
'4_GAGATTCC-TATAGCCT.R2.fastq.gz' : 'be084789b74c26e7afa05f81f773abf5',
'9_CGGCTATG-TATAGCCT.R1.fastq.gz' : '2228c9ae90278551a9929d76bb43938f',
'2_TCCGGAGA-TATAGCCT.R2.fastq.gz' : '42f8f730d750e013cb11970a166fc0be',
'47_TCTCGCGC-GGCTCTGA.R2.fastq.gz' : 'a504324b538d6174f4d3f2378ad69c5b',
'49_ATTACTCG-AGGCGAAG.R2.fastq.gz' : 'b1660f15f0516b559ba62eb7b51f1ede',
'63_CGCTCATT-TAATCTTA.R1.fastq.gz' : '277a8f8648c327f6fd7af46d239cc9af',
'11_TCTCGCGC-TATAGCCT.R1.fastq.gz' : 'cdbd6b70145e89291fa4413d36580d9a',
'43_CTGAAGCT-GGCTCTGA.R1.fastq.gz' : 'db62f720ca855cf91c4215e94bd2b719',
'55_CTGAAGCT-AGGCGAAG.R1.fastq.gz' : 'c797cd5cb0aad64f5c129694473f8980',
'61_ATTACTCG-TAATCTTA.R2.fastq.gz' : '4b0f4edcc29514d857ae5da88b76dfe0',
'63_CGCTCATT-TAATCTTA.R2.fastq.gz' : '97c4dec248bbca09a6aaadcc58dfe5f5',
'83_TCTCGCGC-CAGGACGT.R1.fastq.gz' : '92678150806d01611ac19aa42c582d3c',
'77_ATTCAGAA-CAGGACGT.R1.fastq.gz' : '908d329e29271af4ebeb403483f4c975',
'67_CTGAAGCT-TAATCTTA.R1.fastq.gz' : 'cfd74df04237618c0829da91b2c90d75',
'67_CTGAAGCT-TAATCTTA.R2.fastq.gz' : 'da60f23cc48e5b404ba35d3cc7ad190e',
'50_TCCGGAGA-AGGCGAAG.R1.fastq.gz' : '7d9b4a1eab491f7894dd8b96b6175495',
'14_TCCGGAGA-ATAGAGGC.R1.fastq.gz' : 'b8dbbc7110d4a11881ca3df95fe676ce',
'28_GAGATTCC-CCTATCCT.R1.fastq.gz' : 'd21168432c632bfc3e36aa15281f3568',
'32_TAATGCGC-CCTATCCT.R2.fastq.gz' : 'a0fac5adb1a6ed0a7ef3a3dc02ffac12',
'51_CGCTCATT-AGGCGAAG.R2.fastq.gz' : '96fc11387df459d8f9e1de789747ffcc',
'57_CGGCTATG-AGGCGAAG.R2.fastq.gz' : 'f79e21f2622c089e1f4a2cf0ca3fcda9',
'12_AGCGATAG-TATAGCCT.R1.fastq.gz' : '97a3190b448800515687a64e29f64e8b',
'21_CGGCTATG-ATAGAGGC.R2.fastq.gz' : 'a5923a0074bd66a00fb4eef84441b30b',
'48_AGCGATAG-GGCTCTGA.R1.fastq.gz' : 'c4e687f507b14645522d3a44d535f3bd',
'59_TCTCGCGC-AGGCGAAG.R2.fastq.gz' : '897c765b0815d4210ac4d7a9ac11af2f',
'29_ATTCAGAA-CCTATCCT.R1.fastq.gz' : '363ba2f4c23f881f3b777642cf4c4f67',
'66_GAATTCGT-TAATCTTA.R2.fastq.gz' : '981aa94770099c8a8742d6fce8e4e11c',
'52_TCCGGAGA-GTACTGAC.R2.fastq.gz' : '1fe414036be2005147be0234e616a9ea',
'21_CGGCTATG-ATAGAGGC.R1.fastq.gz' : '30b835e99e1aa9a75ec35fef1f850b01',
'38_TCCGGAGA-GGCTCTGA.R2.fastq.gz' : '58125990979ff5d01ff64182467e2e8c',
'78_GAATTCGT-CAGGACGT.R2.fastq.gz' : '3b871a4c20ce3a283c007ccadaed9ca8',
'4_GAGATTCC-TATAGCCT.R1.fastq.gz' : 'c60b6115aaba2aa09ae532869da98aaa',
'40_GAGATTCC-GGCTCTGA.R1.fastq.gz' : 'bf6ed2580ed47d8baa117fe049ee9f10',
'19_CTGAAGCT-ATAGAGGC.R1.fastq.gz' : 'cf46763bab1ca97c37679a732c5a5047',
'27_CGCTCATT-CCTATCCT.R1.fastq.gz' : 'afbc9b628f5a2d8c24c6e1d206c78dd8',
'74_TCCGGAGA-CAGGACGT.R2.fastq.gz' : '0d85a8159008876fb1de1d8b31fad01e',
'31_CTGAAGCT-CCTATCCT.R1.fastq.gz' : 'b27bdc01dbe704b8d1d654ff7a733c2c',
'46_TCCGCGAA-GGCTCTGA.R2.fastq.gz' : 'cfc9bb4a8f4c6e99daec23e75b88f45d',
'55_CTGAAGCT-AGGCGAAG.R2.fastq.gz' : 'fdb60c7e09b7097b44c6230f9135862d',
'11_TCTCGCGC-TATAGCCT.R2.fastq.gz' : '8adeba842acbe9b192cd75deecfedcff',
'15_CGCTCATT-ATAGAGGC.R1.fastq.gz' : 'df94c3c32fb2827397826c971cb6d702',
'28_GAGATTCC-CCTATCCT.R2.fastq.gz' : 'd5dc881fe6fdbbdf0a968b22711ce7fa',
'7_CTGAAGCT-TATAGCCT.R2.fastq.gz' : '5986da4205ae114ca69b56dd53ed1c78',
'12_AGCGATAG-TATAGCCT.R2.fastq.gz' : '634ef42b65da0cb821e2f91cf4fb0f5c',
'18_GAATTCGT-ATAGAGGC.R2.fastq.gz' : '3656a7ed3778c8d07a014dd3b242baff',
'81_CGGCTATG-CAGGACGT.R1.fastq.gz' : '4c78ef7fc3b28fcab7b6a4f347fe89bd',
'25_ATTACTCG-CCTATCCT.R1.fastq.gz' : '950b32b562d3f9c650d3ab9d3b820347',
'80__CTGAAGCT-CAGGACGT.R1.fastq.gz' : '74ed79541c3ce22a17e53881d2a128af',
'74_TCCGGAGA-CAGGACGT.R1.fastq.gz' : '5f66d82883c975f78461d3f3b9e00f08',
'70_TCCGCGAA-TAATCTTA.R2.fastq.gz' : 'fa5ca691bb36a79aae2db470c222146a',
'52_TCCGGAGA-GTACTGAC.R1.fastq.gz' : 'f0d9e4dc4a73bdc4a71c937abaadb093',
'33_CGGCTATG-CCTATCCT.R1.fastq.gz' : 'eaeef1e9299ae58f1e365d9e10473a7f',
'53_ATTCAGAA-AGGCGAAG.R1.fastq.gz' : 'a53cad0d8569a11631e8618473c6ff65',
'81_CGGCTATG-CAGGACGT.R2.fastq.gz' : '7de49a10f2495a05d4bfa04eaef5a730',
'64_GAGATTCC-TAATCTTA.R2.fastq.gz' : 'db580259cb924e6433cbce1a0335e626',
'39_CGCTCATT-GGCTCTGA.R2.fastq.gz' : '3b2ed086b74a344697fed14456464832',
'38_TCCGGAGA-GGCTCTGA.R1.fastq.gz' : 'a509e769bf34eb36048330dd6e67abfd',
'83_TCTCGCGC-CAGGACGT.R2.fastq.gz' : '2ed4792d6f3b4f05661afa117f297f50',
'1_ATTACTCG-TATAGCCT.R2.fastq.gz' : '2546393f75f076d3a0e9b89b4691b8d2',
'27_CGCTCATT-CCTATCCT.R2.fastq.gz' : '9a57324a566fa2ca2ba097dfd4c4e1e4',
'68_TAATGCGC-TAATCTTA.R1.fastq.gz' : 'd019c6130e27ff46d4e96cfde0a21316',
'5_ATTCAGAA-TATAGCCT.R1.fastq.gz' : 'a823026ec235c9621d24a8d1f3a4f23f',
'73_ATTACTCG-CAGGACGT.R1.fastq.gz' : '8a16c765ceb109ea04c6eab40c4b6eb2',
'82_TCCGCGAA-CAGGACGT.R2.fastq.gz' : '8ae9df0036fd28159f50c616684931fe',
'80_ATTACTCG-GTACTGAC.R1.fastq.gz' : '86a87fecc811014f57caee1cbb04ae72',
'13_ATTACTCG-ATAGAGGC.R1.fastq.gz' : '4f22132edaae064274360cfd53ceca65',
'68_TAATGCGC-TAATCTTA.R2.fastq.gz' : 'f03a49a9b885ee939f815b874301c429',
'37_ATTACTCG-GGCTCTGA.R1.fastq.gz' : '33c0c71d963c02005aa6641137b4855a',
'76_GAGATTCC-CAGGACGT.R2.fastq.gz' : '2cee3785a0dfef7dba399d3a5c4e11bf',
'41_ATTCAGAA-GGCTCTGA.R1.fastq.gz' : '5a9a1af2e47310fed2f3081b9c853e3e',
'18_GAATTCGT-ATAGAGGC.R1.fastq.gz' : '30bb70a01458d68b3a3088b9e9c952c0',
'36_AGCGATAG-CCTATCCT.R1.fastq.gz' : '8c447827e819b3448c6849a0e5d28d76',
'23_TCTCGCGC-ATAGAGGC.R1.fastq.gz' : '4c65b1add12466c9838d8e8c256efeee',
'62_TCCGGAGA-TAATCTTA.R2.fastq.gz' : 'a28185e8e72f628c98c90a68edeb27fd',
'48_AGCGATAG-GGCTCTGA.R2.fastq.gz' : 'aef9959a77ddd91efa5189bf0af045d6',
'42_GAATTCGT-GGCTCTGA.R1.fastq.gz' : '52db5d7e668872bdc6914521c1a12b37',
'78_GAATTCGT-CAGGACGT.R1.fastq.gz' : '778d2893ae4b617e253bca456a36ed90',
'54_GAATTCGT-AGGCGAAG.R2.fastq.gz' : 'c8658b0fe61b7f01c51ddca7cf7a076d',
'72_AGCGATAG-TAATCTTA.R2.fastq.gz' : '8b03945a4b2439d20c2ac137ccdb368a',
'37_ATTACTCG-GGCTCTGA.R2.fastq.gz' : 'b54d8cd9eb0388bf1847a617bd83b25c',
'69_CGGCTATG-TAATCTTA.R2.fastq.gz' : '109a4518e49f5c2b73ee1047ac91a665',
'41_ATTCAGAA-GGCTCTGA.R2.fastq.gz' : '657752aaa71a9e4035e5940fac3239f3',
'64_GAGATTCC-TAATCTTA.R1.fastq.gz' : '0c24baf461f72523c78036834d34a7cf',
'66_GAATTCGT-TAATCTTA.R1.fastq.gz' : 'd08ff5ac96c7f54c7c1067c519df4090',
'84_AGCGATAG-CAGGACGT.R2.fastq.gz' : 'e8f6546ba28a9d064f55233d873e0c5a',
'10_TCCGCGAA-TATAGCCT.R1.fastq.gz' : '7691ce38b86c9a25124ea14d0b4b015a',
'59_TCTCGCGC-AGGCGAAG.R1.fastq.gz' : '3f3af00b1c82efa936630a3299add8f8',
'19_CTGAAGCT-ATAGAGGC.R2.fastq.gz' : '9bad5977373710f7d1ec87c451f2759f',
'10_TCCGCGAA-TATAGCCT.R2.fastq.gz' : '19602ce83ce1d79cda18a84089aeef8d',
'80_ATTACTCG-GTACTGAC.R2.fastq.gz' : '6d7a89d3af93099e63141c51d06c97a4',
'58_TCCGCGAA-AGGCGAAG.R2.fastq.gz' : '132d45be0d330d4b33d000e1559c2f03',
'15_CGCTCATT-ATAGAGGC.R2.fastq.gz' : '3d67773e7a71094f7eb40b5ff8f752e4',
'69_CGGCTATG-TAATCTTA.R1.fastq.gz' : '4407047d7ce1ad84ea9ac8a1c0b7051e',
'53_ATTCAGAA-AGGCGAAG.R2.fastq.gz' : 'd5a36294cb6acf4fd013878a9d636c81',
'65_ATTCAGAA-TAATCTTA.R1.fastq.gz' : 'dafb2f44ba40bf35c26dd6f693f8bc8e',
'61_ATTACTCG-TAATCTTA.R1.fastq.gz' : 'f2ad471da3fe2dbf7f57328c32c0d2d6',
'51_CGCTCATT-AGGCGAAG.R1.fastq.gz' : '72a2833f9c6c50f8277e98ef4d9d8242',
'73_ATTACTCG-CAGGACGT.R2.fastq.gz' : '686051a7db1595e2cc3fdecdc41d4410',
'75_CGCTCATT-CAGGACGT.R2.fastq.gz' : '7eee203dfdbce0ee02d9dac2a3b1c132',
'16_GAGATTCC-ATAGAGGC.R2.fastq.gz' : '05d51cd4e0f0b2bf805b5b7af6c9fa3c',
'23_TCTCGCGC-ATAGAGGC.R2.fastq.gz' : 'bd60762c8872bac64a6fe938c6b44ea6',
'6_GAATTCGT-TATAGCCT.R2.fastq.gz' : '048700b78ff0fe35587edca3a58b5d19',
'17_ATTCAGAA-ATAGAGGC.R1.fastq.gz' : '3c3ad43c8d483cbc5d7617187bd5f95b',
'82_TCCGCGAA-CAGGACGT.R1.fastq.gz' : 'fe98b308e02a4733ef73a91ec373206b',
'14_TCCGGAGA-ATAGAGGC.R2.fastq.gz' : 'fa0abee78a5efbb5d53139e627512751',
'33_CGGCTATG-CCTATCCT.R2.fastq.gz' : '125258a442a337984ab76c117311d6dd',
'3_CGCTCATT-TATAGCCT.R2.fastq.gz' : '28b1fd276a1ca4d52a55f99d68ccde8a',
'2_TCCGGAGA-TATAGCCT.R1.fastq.gz' : 'f68a9f35e992623fd5b6d8370aaa57ae',
'84_AGCGATAG-CAGGACGT.R1.fastq.gz' : '0572d39a8af33169fc5ab22a05444229',
'24_AGCGATAG-ATAGAGGC.R2.fastq.gz' : '5622171943ee270568059395010bc032',
'26_TCCGGAGA-CCTATCCT.R1.fastq.gz' : 'f9a2ce699fa6b42f644ec55064a5bbb3',
'35_TCTCGCGC-CCTATCCT.R2.fastq.gz' : '462f8dd548bb762fd73a01e1309db8eb',
'76_GAGATTCC-CAGGACGT.R1.fastq.gz' : '35b6f71ebf588e4157de36c7524bbf6d',
'79__TAATGCGC-CAGGACGT.R1.fastq.gz' : 'c0ff4b17db35faac8742327c6bb0abcc',
'24_AGCGATAG-ATAGAGGC.R1.fastq.gz' : '3c45d1aaa0191052af93df0427d33958',
}

        
    def setUp(self):
        
        self.workingdir = os.path.join(os.getcwd(),'run')
        os.makedirs(self.workingdir)
        
        # Create the necessary iggy settings files
        pipestr = '''
###
## iggypipe preferences
###

# Directory for analysis results and logs.
IGGYPIPE_DIR: /n/regal/rc_admin/mclamp/iggypipeout/

# Logging level.
# Choices: [info, debug]
LOGGING_LEVEL: debug

# Database type.
# Choices: [sqlite, mysql]
DB_TYPE: mysql

# If DB_TYPE is sqlite, mysql settings can be ignored.
MYSQL_HOST: db-internal

MYSQL_DB: iggypipe_mclamp

MYSQL_USER: iggy

MYSQL_PASS: 98smms76

# Debug mode.
DEBUG: False        
'''
        f = open(os.path.join(self.workingdir,'iggypipe_settings.yaml'), 'w')
        f.write(pipestr)
        f.close()
        
        refstr = '''
####
##  IggyRef preferences
####

# Directory for genomes and databases 
IGGYREF_REPOSITORY_DIR: '/n/regal/informatics_public/ref/'

# Level of logging detail (info or debug)
LOGGING_LEVEL: debug

# Database type (sqlite or mysql)
DB_TYPE: mysql

# Note, if DB_TYPE is sqlite, then the mysql settings below can be ignored:
MYSQL_USER: iggy
MYSQL_HOST: db-internal
MYSQL_DB: iggyref
MYSQL_PASS: 98smms76

# Debug mode (In debug mode, files are not copied to REPOSITORY_DIR)
DEBUG: False

# EBI collection choices are interpro, pfam
EBI_COLLECTIONS: [interpro, pfam]

# Ensembl collection choices are human, fruitfly, worm, yeast
ENSEMBL_COLLECTIONS: [human, fruitfly, worm, yeast]

# NCBI collection choices are nr, nt, refseq_genomic, refseq_protein, refseq_rna, swissprot
NCBI_COLLECTIONS: [nr, nt, refseq_genomic, refseq_protein, refseq_rna, swissprot]

# UCSC collection choices are chicken_galGal3, chicken (most recent), fruitfly, human, 
# mouse, rat, worm, yeast, zebrafinch
UCSC_COLLECTIONS: [chicken_galGal3, chicken, fruitfly, human, mouse, rat, worm, yeast, zebrafinch]

# The sole Uniprot collection choice is uniref100
UNIPROT_COLLECTIONS: [uniref100]
'''
        f = open(os.path.join(self.workingdir,'iggyref_settings.yaml'), 'w')
        f.write(refstr)
        f.close()
        
        
        
        #
        # Setup the seqprep preferences
        #
        self.prefs = {
            'watchersfile'    : '/n/informatics/saved/seqprep_watchers_list.txt',
            'usersfile'       : '/n/informatics/saved/iggyseq_users_list.txt',
            'primaryparent'   : '/n/informatics/git/testdata',
            'logdirparent'    : os.path.join(self.workingdir,'seqprep_log'),
            'processingparent' : os.path.join(self.workingdir,'analysis_in_progress'),
            'finishingparent' : os.path.join(self.workingdir,'analysis_finished'),
            'finalparent'     : os.path.join(self.workingdir,'ngsdata'),
            'seqstatshistdir' : os.path.join(self.workingdir,'seqstats_bkup'),
            'seqstatslogfile' : os.path.join(self.workingdir,'seqprep_log','seqstatslog.txt'),   
            'machinetype'     :"{'NS500422': 'NextSeq', 'SN343': 'HiSeq', 'D00365': 'HiSeq', 'NS500305': 'NextSeq'}",
            'tileregex'       : "s_1_1308",         
        }
        for d in ['logdirparent','processingparent','finishingparent','finalparent','seqstatshistdir']:
            os.makedirs(self.prefs[d])
            
            
        self.preffile = os.path.join(self.workingdir,'iggyseq_settings.yaml')
        preftext = """
VERBOSE: True
PRIMARY_PARENT: {primaryparent}
MACHINE_TYPE: {machinetype}
USERS_FILE: {usersfile}
WATCHERS_FILE: {watchersfile}
LOGDIR_PARENT: {logdirparent}
PROCESSING_PARENT: {processingparent}
FINISHING_PARENT: {finishingparent}
FINAL_PARENT: {finalparent}
SEQPREP_NUM_MISMATCHES: 0
SEQPREP_NUM_THREADS: 8
SEQPREP_IGNORE_MISSING_BCL: True
SEQPREP_IGNORE_MISSING_CONTROL: True
SEQPREP_WITH_FAILED_READS: False
SEQPREP_TILE_REGEX: {tileregex}
SEQPREP_DB_STORE: False
NEXTSEQ_MASK_SHORT_ADAPTER_READS: None
NEXTSEQ_SUPPRESS_ADAPTER_TRIMMING: False
NEXTSEQ_MIN_TRIMMED_READ_LENGTH: 0
SLURM_TIME: '48:00:00'
SLURM_MEM: 10000
SLURM_PARTITION: general
SEQSTATS_HIST_DIR: {seqstatshistdir}
SEQSTATS_LOGFILE: {seqstatslogfile}
""".format(**self.prefs)
    
        f = open(self.preffile,'w')
        f.write(preftext)
        f.close()


    def tearDown(self):
        shutil.rmtree(self.workingdir)


    def testRun(self):
        
        #
        # Execute a seqprep run
        #
        runpath = os.path.join(self.prefs['primaryparent'])
        cmd = "seqprep -p %s %s" % (runpath,self.runname)
        
        returncode = os.system(cmd)
        self.assertEqual(returncode, 0, "seqprep %s returned non-zero" % cmd)       
        
        #
        # Check md5s of files in one of the lane directories
        #
        fastqpath = os.path.join(self.prefs['finalparent'],self.runname,'Lane1.indexlength_8_8','Fastq')
        checksumfilename = os.path.join(fastqpath,"checksum.txt")
        checksumfile = open(checksumfilename,'w')
        for fname, md5sum in self.md5s.iteritems():
            fqfile = os.path.join(fastqpath,fname)
            self.assertTrue(os.path.isfile(fqfile),"%s does not exist" % fqfile)
            checksumfile.write("%s  %s\n" % (md5sum,fname))
        checksumfile.close()
        cmd = "cd %s && md5sum -c checksum.txt" % fastqpath
        returncode = os.system(cmd)
        self.assertEqual(returncode,0,"checksum command %s failed" % cmd)
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
